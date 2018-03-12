#!/bin/env python

import re
import time
import smtplib
import asyncio
import base64
import datetime
import logging
import importlib

from collections import defaultdict

import email
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from email.utils import localtime
from email.headerregistry import Address, HeaderRegistry, AddressHeader

import aiodns
from aiodns.error import DNSError

from byemail import mailutils
from byemail.conf import settings
from byemail.mailstore import storage
from byemail.account import account_manager

logger = logging.getLogger(__name__)


EMPTYBYTES = b''
COMMASPACE = ', '
CRLF = b'\r\n'
NLCRE = re.compile(br'\r\n|\r|\n')

async def enrich(msg, from_addr, to_addrs):
    msg['type'] = 'mail'

    msg['original-sender'] = from_addr
    msg['original-recipients'] = to_addrs

    # First define uid
    msg['uid'] = uuid.uuid4().hex

    msg['account'] = account.name

    msg['incoming'] = incoming
    msg['unread'] = incoming

class MsgHandler:

    def __init__(self, loop=None):
        super().__init__()
        self.loop = loop or asyncio.get_event_loop()

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

        # TODO handle message refused when spam or something
        await self.local_delivery(envelope.rcpt_tos, server, session, envelope)

        return '250 Message accepted for delivery'

    async def apply_middlewares(self, msg, from_addr, to_addrs):
        for middleware in settings.INCOMING_MIDDLEWARES:
            try:
                module, _, func = middleware.rpartition(".")
                print(func, module)
            except ModuleNotFoundError:
                logger.error("Module %s can't be loaded !", middleware)
                raise
            else:
                mod = importlib.import_module(module)
                await getattr(mod, func)(msg, from_addr, to_addrs)

    async def local_delivery(self, rcpt_tos, server, session, envelope):
        for to in rcpt_tos:
            logger.info('Local delivery for %s' % to)

            try:
                msg = BytesParser(policy=policy.default).parsebytes(envelope.content)
                account = account_manager.get_account_for_address(to)
                logger.info('Message delivered to account %s', account.name)

                msg_data = await mailutils.extract_data_from_msg(msg)

                await self.apply_middlewares(msg_data, envelope.mail_from, [to])
                
                stored_msg = await storage.store_msg(
                    msg_data, 
                    account=account, 
                    from_addr=envelope.mail_from, 
                    to_addrs=envelope.rcpt_tos
                )
                
            except:
                import traceback; traceback.print_exc()
                #import ipdb; ipdb.set_trace()
                await self.save_failed_msg(session, envelope) # TODO handle multiple toos
                print('Error for current message')

            return '250 Message accepted for delivery'


class MxRecord(object):

    def __init__(self, domain, loop=None):
        self.domain = domain
        self._records = None
        self._expiration = 0
        self.loop = loop or asyncio.get_event_loop()
        self.resolver = aiodns.DNSResolver(loop=self.loop)

    @property
    def expired(self):
        return not self._expiration or time.time() >= self._expiration

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
            try:
                return await self._resolve_a()
            except DNSError as exc:
                raise



class MsgSender():

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

    def group_by_fqdn(self, address):
        """ Group mails by domains """

        result = defaultdict(list)
        for add in address:
            fqdn = add.split('@')[1]
            result[fqdn].append(add)

        return result

    async def apply_middlewares(self, msg, from_addr, to_addrs):
        for middleware in settings.OUTGOING_MIDDLEWARES:
            try:
                module, _, func = middleware.rpartition(".")
                print(func, module)
            except ModuleNotFoundError:
                logger.error("Module %s can't be loaded !", middleware)
                raise
            else:
                mod = importlib.import_module(module)
                await getattr(mod, func)(msg, from_addr, to_addrs)

    async def send(self, msg, from_addr, to_addrs):
        """ Relay message to other party """

        status = {}

        await self.apply_middlewares(msg, from_addr, to_addrs)

        for fqdn, addresses in self.group_by_fqdn(to_addrs).items():
            try:
                mxs = await MxRecord(fqdn).get()
            except DNSError as e:
                logger.warning("MX for %s not found" % fqdn)
                for addr in addresses:
                    status[addr] = {
                        'status': 'ERROR',
                        'reason': 'MX_NOT_FOUND'
                    }
                continue

            for _, mx in mxs:
                try_another_mx = False
                try:
                    result = await self._relay_to(mx, from_addr, addresses, msg)
                    # Here result is good for at least one recipient
                    for addr in addresses:
                        addr_status = result[addr]
                        if addr_status[0].startswith('25'):
                            status[addr] = {
                                'status': 'DELIVERED',
                                'stmp_info': addr_status
                            }
                        else:
                            status[addr] = {
                                'status': 'ERROR',
                                'reason': 'SMTP_ERROR',
                                'smtp_info': addr_status
                            }
                except smtplib.SMTPException as e:
                    # Failed for all recipients
                    for addr in addresses:
                        status[addr] = {
                            'status': 'ERROR',
                            'reason': 'SMTP_ERROR',
                            'smtp_info': e.recipients[addr]
                        }
                except TimeoutError:
                    # Can't connect
                    try_another_mx = True
                    for addr in addresses:
                        status[addr] = {
                            'status': 'ERROR',
                            'reason': 'MX_TIMEOUT'
                        }
                    logger.exception('Timeout error')
                except:
                    for addr in addresses:
                        status[addr] = {
                            'status': 'ERROR',
                            'reason': 'UNKNOWN_ERROR'
                        }
                    logger.exception('Unknown error while sending to %s', mx)

                if not try_another_mx:
                    break
        
        return status

    async def _relay_to(self, hostname, from_addr, to_addrs, msg):
        logger.info("Try to relay mail to %s from %s to %s", hostname, from_addr, str(to_addrs))
        return await self.loop.run_in_executor(
            None, 
            self._sendmsg, 
            hostname, 
            25, 
            msg, 
            from_addr, 
            to_addrs
        )

    def _sendmsg(self, host, port, msg, from_addr, to_addrs):
        logger.info("Send mail from %s to %s", from_addr, to_addrs)
        if settings.DEBUG:
            print("Should send...")
            print(msg)
            result = {}
            for addr in to_addrs:
                result[addr] = ('250', 'Delivered')
        else:
            with smtplib.SMTP(host=host, port=port) as smtp:
                return smtp.send_message(msg, from_addr=from_addr, to_addrs=to_addrs)