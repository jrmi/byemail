import time
import asyncio
import smtplib
import logging
import importlib

import email
from collections import defaultdict
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from email.utils import localtime
from email.headerregistry import Address, HeaderRegistry, AddressHeader

import aiodns
from aiodns.error import DNSError

from byemail.mailstore import storage
from byemail import mailutils
from byemail.conf import settings

logger = logging.getLogger(__name__)

class MxRecord(object):

    def __init__(self, domain, loop=None):
        self.domain = domain
        self._records = None
        self._expiration = 0
        self.loop = loop or asyncio.get_event_loop()
        self.resolver = aiodns.DNSResolver(loop=self.loop)

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

    @property
    def expired(self):
        return not self._expiration or time.time() >= self._expiration

class MailSender():

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

    def group_by_fqdn(self, address):
        """ Group mails by domains """

        result = defaultdict(list)
        for add in address:
            fqdn = add.split('@')[1]
            result[fqdn].append(add)

        return result

    async def send(self, msg, from_addr, to_addrs):
        """ Relay message to other party """

        status = {}

        for middleware in settings.MTA_MIDDLEWARES:
            try:
                module, _, func = middleware.rpartition(".")
                print(func, module)
            except ModuleNotFoundError:
                logger.error("Module %s can't be loaded !", middleware)
                raise
            else:
                mod = importlib.import_module(module)
                getattr(mod, func)(msg, from_addr, to_addrs)


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
