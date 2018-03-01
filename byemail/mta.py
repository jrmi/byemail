import time
import asyncio
import smtplib
import logging

import email
from collections import defaultdict
from email import policy
from email.parser import BytesParser
from email.message import EmailMessage
from email.utils import localtime
from email.headerregistry import Address, HeaderRegistry, AddressHeader

import aiodns
from aiodns.error import DNSError

from leefmail.mailstore import storage
from leefmail import mailutils

logger = logging.getLogger(__name__)

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

    '''async def make_msg_from_data(self, account, data):
        content = data['content']
        subject = data['subject']

        tos = [mailutils.parse_email(a['address']) for a in data['recipients'] if a['type'] == 'to']
        ccs = [mailutils.parse_email(a['address']) for a in data['recipients'] if a['type'] == 'cc']

        #from_addr = Address(display_name=data['from']['display_name'], addr_spec=data['from']['addr_spec'])
        from_addr = mailutils.parse_email(account.address)

        # To have a correct address header
        header_registry = HeaderRegistry()
        header_registry.map_to_type('To', AddressHeader)
        msg = EmailMessage(policy.EmailPolicy(header_factory=header_registry))

        msg.set_content(content)
        msg['From'] = from_addr
        msg['Subject'] = subject

        if tos:
            msg['To'] = tos
        if ccs:
            msg['Cc'] = ccs

        msg['Date'] = localtime()

        return msg'''


    async def send(self, msg, from_addr, to_addrs):
        """ Relay message to other party """
        for fqdn, addresses in self.group_by_fqdn(to_addrs).items():
            mxs = await MxRecord(fqdn).get()
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
        logger.info("Send mail from %s to %s", from_addr, to_addrs)
        with smtplib.SMTP(host=host, port=port) as smtp:
            logger.debug("DRY-RUN: Should send mail here !!!")
            #smtp.send_message(msg, from_addr=from_addr, to_addrs=to_addrs)
