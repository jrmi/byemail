#!/bin/env python

import re
import asyncio
import base64
import datetime
import logging

from email import policy
from email.parser import BytesParser

from leefmail.conf import settings
from leefmail.mailstore import storage
from leefmail.account import account_manager


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

        if account_manager.is_local_address(address):
            envelope.rcpt_tos.append(address)
            return '250 OK'

        return '550 not relaying to that domain'

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

        await self.local_delivery(envelope.rcpt_tos, server, session, envelope)

        return '250 Message accepted for delivery'

    async def local_delivery(self, rcpt_tos, server, session, envelope):
        for to in rcpt_tos:
            logger.info('Local delivery for %s' % to)

            try:
                #msg = await self.parse_msg(session, envelope)
                msg = BytesParser(policy=policy.default).parsebytes(envelope.content)
                account = account_manager.get_account_for_address(envelope.mail_from)
                logger.info('Message delivered to account %s', account.name)
                msg_data = await storage.store_msg(msg, account=account, from_addr=envelope.mail_from, to_addrs=envelope.rcpt_tos)
            except:
                import traceback; traceback.print_exc()
                #import ipdb; ipdb.set_trace()
                await self.save_failed_msg(session, envelope) # TODO handle multiple toos
                print('Error for current message')

            return '250 Message accepted for delivery'
