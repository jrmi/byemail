#!/bin/env python

import os
import re
import asyncio
import base64
import datetime
import mimetypes
import smtplib
import logging
import time
from collections import defaultdict

import email
from email import policy
from email.parser import BytesParser

import aiodns
from aiodns.error import DNSError

from tinydb import Query

from leefmail.conf import settings
from leefmail.mailstore import storage


logger = logging.getLogger(__name__)

EMPTYBYTES = b''
COMMASPACE = ', '
CRLF = b'\r\n'
NLCRE = re.compile(br'\r\n|\r|\n')

class MSGHandler:

    def __init__(self):
        super().__init__()

        loop = asyncio.get_event_loop()

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        #import ipdb; ipdb.set_trace()
        print(session.peer)
        print(address)

        if self.is_local_address(address):
            return '250 OK'

        '''if session.peer[0] != '127.0.0.1': # Select only local connections

        else:
            envelope.rcpt_tos.append(address)
            return '250 OK'''

        return '550 not relaying to that domain'

    async def parse_msg(self, session, envelope):
        """ Parse message and envelope to extract maximum of metadata. """

        msg = BytesParser(policy=policy.default).parsebytes(envelope.content)

        body = msg.get_body(('html', 'plain',))

        #import ipdb; ipdb.set_trace()

        msg_out = {
            'type': 'mail',
            'status': 'delivered',
            'peer': session.peer,
            'host_name': session.host_name,
            'envelope_from': envelope.mail_from,
            'envelope_tos': envelope.rcpt_tos,
            'subject': msg['Subject'],
            'received': datetime.datetime.now().isoformat(),
            'content': envelope.content,
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
            'body-type': body.get_content_type(),
            'body-charset': body.get_content_charset(),
            'body': body.get_content(),
            'attachments': []
        }

        for ind, att in enumerate(msg.iter_attachments()):
            msg_out['attachments'].append({
                'index': ind,
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

        await storage.store_bad_msg(to_save)

    async def handle_DATA(self, server, session, envelope):
        print('Message From: %s, To: %s' % (envelope.mail_from, envelope.rcpt_tos))

        '''local_deliveries = []
        relay_deliveries = []
        for to in envelope.rcpt_tos:
            if self.is_local_address(to):
                local_deliveries.append(to)
            else:
                relay_deliveries.append(to)'''

        await self.local_delivery(envelope.rcpt_tos, server, session, envelope)
        #await self.relay(relay_deliveries, server, session, envelope)

        return '250 Message accepted for delivery'

    def is_local_address(self, address):
        return any((address.endswith(suffix) for suffix in settings.ACCEPT))

    async def local_delivery(self, rcpt_tos, server, session, envelope):
        for to in rcpt_tos:
            print('Local delivery for %s' % to)

            try:
                msg = await self.parse_msg(session, envelope)
            except:
                import traceback; traceback.print_exc()
                #import ipdb; ipdb.set_trace()
                await self.save_failed_msg(session, envelope) # TODO handle multiple toos
                print('Error for this message')
            else:
                await storage.store_msg(msg)

            return '250 Message accepted for delivery'


class MxRecord(object):

    def __init__(self, domain):
        self.domain = domain
        self._records = None
        self._expiration = 0
        loop = asyncio.get_event_loop()
        self.resolver = aiodns.DNSResolver(loop=loop)

    async def get(self):
        if self.expired:
            self._records, self._expiration = await self._resolve()
        if not self._records:
            msg = 'No usable DNS records found: %s' % self.domain
            raise ValueError(msg)
        return self._records

    async def _resolve_a(self):
        answer = await self.resolver.query(self.domain, 'A')
        expiration = 0
        now = time.time()
        ret = []
        for rdata in answer:
            ret.append((0, self.domain))
            expiration = max(expiration, now + rdata.ttl)
        return ret, expiration

    async def _resolve_mx(self):
        answer = await self.resolver.query(self.domain, 'MX')
        expiration = 0
        now = time.time()
        ret = []
        for rdata in answer:
            for i, rec in enumerate(ret):
                if rec[0] > rdata.priority:
                    ret.insert(i, (rdata.priority, str(rdata.host)))
                    break
            else:
                ret.append((rdata.priority, str(rdata.host)))
            expiration = max(expiration, now + rdata.ttl)
        return ret, expiration

    async def _resolve(self):
        try:
            return await self._resolve_mx()
        except DNSError:
            logger.exception('Error while resolving MX for %s', self.domain)
            try:
                return await self._resolve_a()
            except DNSError as exc:
                raise

    @property
    def expired(self):
        return not self._expiration or time.time() >= self._expiration

class MailSender():

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def group_by_fqdn(self, address):
        """ Group mails by domains """

        result = defaultdict(lambda: [])
        for add in address:
            fqdn = add.split('@')[1]
            result[fqdn].append(add)

        return result

    async def send(self, msg, from_addr, to_addrs):

        for fqdn, addresses in self.group_by_fqdn(to_addrs).items():
            print('fqdn:', fqdn)
            mxs = await MxRecord(fqdn).get()
            print('Mx found', mxs)
            for _, mx in mxs:
                try:
                    await self._relay_to(mx, from_addr, addresses, msg)
                    break
                except:
                    logger.exception('Fail to connect to %s', mx)

    async def _relay_to(self, hostname, from_addr, to_addrs, msg):
        logger.info("Try to relay mail to %s from %s to %s", hostname, from_addr, str(to_addrs))
        port = 25
        refused = {}
        try:
            await self.loop.run_in_executor(None, self._sendmsg, hostname, port, msg, from_addr, to_addrs)
        except smtplib.SMTPRecipientsRefused as e:
            logger.warning('got SMTPRecipientsRefused %s', e.recipients)
            refused = e.recipients
        except TimeoutError:
            logger.exception('Timeout error')
        except (OSError, smtplib.SMTPException) as e:
            logger.exception('got %s', e.__class__)
            # All recipients were refused.  If the exception had an associated
            # error code, use it.  Otherwise, fake it with a non-triggering
            # exception code.
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            for r in to_addrs:
                refused[r] = (errcode, errmsg)
        return refused

    def _sendmsg(self, host, port, msg, from_addr, to_addrs):
        with smtplib.SMTP(host=host, port=port) as smtp:
            #smtp.login('jrmi', 'password') # TODO Auth not supported for now.
            #smtp.send_message(msg, from_addr=from_addr, to_addrs=to_addrs)
            print("DRY-RUN: Should send mail here !!!")
