#!/bin/env python

import os
import asyncio
import base64
import datetime
import mimetypes
import uuid

import email
from email import policy
from email.parser import BytesParser


from tinydb import Query

from leefmail import settings, store

class MSGHandler:

    def __init__(self):
        super().__init__()

        loop = asyncio.get_event_loop()

        self.db = loop.run_until_complete(store.get_db())

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        for suffix in settings.ACCEPT:
            if address.endswith(suffix):
                envelope.rcpt_tos.append(address)
                return '250 OK'
        return '550 not relaying to that domain'

    async def parse_msg(self, session, envelope):
        """ Parse message and envelope to extract maximum of metadata. """

        msg = BytesParser(policy=policy.default).parsebytes(envelope.content)

        body = msg.get_body()

        msg_out = {
            'id': uuid.uuid4().hex,
            'type': 'mail',
            'status': 'delivered',
            'peer': session.peer,
            'host_name': session.host_name,
            'envelope_from': envelope.mail_from,
            'envelope_tos': envelope.rcpt_tos,
            'subject': msg['Subject'],
            'received': datetime.datetime.now().isoformat(),
            'data': base64.b64encode(envelope.content).decode('utf-8'),
            'from': msg['From'].addresses[0],
            'tos': list(msg['To'].addresses),
            'original-to': msg['X-Original-To'],
            'delivered-to': msg['Delivered-To'],
            'dkim-signature': msg['DKIM-Signature'],
            'message-id': msg['Message-ID'],
            'domain-signature': msg['DomainKey-Signature'],
            'date': msg['Date'].datetime,
            'return': msg['Return-Path'] or msg['Reply-To'],
            'in-thread': False,
            'main-body-type': body.get_content_type(),
            'attachments': []
        }

        #import ipdb; ipdb.set_trace()

        for att in msg.iter_attachments():
            msg_out['attachments'].append({
                'type': att.get_content_type(),
                'filename': att.get_filename()
            })

        if msg['Thread-Topic']:
            msg_out['in_thread'] = True
            msg_out['thread-topic'] = msg['Thread-Topic']
            msg_out['thread-index'] = msg['Thread-index']

        return msg_out

    async def save_failed_msg(self, session, envelope):
        """ To handle msg that failed to parse """
        msg = BytesParser(policy=policy.default).parsebytes(envelope.content)

        to_save = {
            'type': 'mail',
            'status': 'error',
            'peer': session.peer,
            'host_name': session.host_name,
            'from': envelope.mail_from,
            'tos': envelope.rcpt_tos,
            'subject': msg['Subject'],
            'received': datetime.datetime.now().isoformat(),
            'data': base64.b64encode(envelope.content).decode('utf-8'),
        }

        self.db.insert(to_save)

    async def save_in_db(self, msg):
        self.db.insert(msg)

    async def update_mailbox(self, msg):
        Mailbox = Query()
        msg_from = msg['from'].addr_spec

        # Get mailbox if exists
        mailbox = await store.get_or_create((Mailbox.type == 'mailbox') & (Mailbox['from'] == msg_from), {
            'type': 'mailbox',
            'from': msg_from,
            'last_message': msg['date'],
            'messages': [],
        })

        '''results = self.db.search((Mailbox.type == 'mailbox') & (Mailbox['from'] == msg_from))
        if len(results) < 1: # Doesn't exists
            # Let's create one
            mailbox = {
                'type': 'mailbox',
                'from': msg_from,
                'last_message': msg['date'],
                'messages': [],
            }
            self.db.insert(mailbox)
        else:
            mailbox = results[0]'''

        # Update last_message date
        if mailbox['last_message'] < msg ['date']:
            mailbox['last_message'] = msg['date']

        mailbox['messages'].append({
            'id': msg['id'],
            'date': msg['date'],
            'subject': msg['subject']
        })

        self.db.update(mailbox, (Mailbox.type == 'mailbox') & (Mailbox['from'] == msg_from))

    async def handle_DATA(self, server, session, envelope):
        
        print('Message From: %s, To: %s' % (envelope.mail_from, envelope.rcpt_tos))
        
        try:
            msg = await self.parse_msg(session, envelope)
        except:
            import traceback; traceback.print_exc()
            import ipdb; ipdb.set_trace()
            await self.save_failed_msg(session,envelope)
            print('Error for this message')
        else:
            await self.save_in_db(msg)
            await self.update_mailbox(msg)

        return '250 Message accepted for delivery'
