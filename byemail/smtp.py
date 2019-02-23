#!/bin/env python

import re
import uuid
import time
import smtplib
import asyncio
import base64
import datetime
import logging

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
from byemail.storage import storage
from byemail.account import account_manager
from byemail import push

logger = logging.getLogger(__name__)


EMPTYBYTES = b""
COMMASPACE = ", "
CRLF = b"\r\n"
NLCRE = re.compile(br"\r\n|\r|\n")


class MsgHandler:
    def __init__(self, loop=None):
        super().__init__()
        self.loop = loop or asyncio.get_event_loop()

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):

        if account_manager.is_local_address(address):
            envelope.rcpt_tos.append(address)
            return "250 OK"

        return "550 not relaying to that domain"

    async def save_failed_msg(self, session, envelope):
        """ To handle msg that failed to parse """
        msg = BytesParser(policy=policy.default).parsebytes(envelope.content)

        to_save = {
            "status": "error",
            "peer": session.peer,
            "host_name": session.host_name,
            "from": envelope.mail_from,
            "tos": envelope.rcpt_tos,
            "subject": msg["Subject"],
            "received": datetime.datetime.now().isoformat(),
            "data": base64.b64encode(envelope.content).decode("utf-8"),
        }

        await storage.store_bad_msg(to_save)

    async def handle_DATA(self, server, session, envelope):
        logger.info("Message From: %s, To: %s", envelope.mail_from, envelope.rcpt_tos)

        # TODO handle message refused when spam or something with middleware ?
        await self.local_delivery(envelope.rcpt_tos, server, session, envelope)

        return "250 Message accepted for delivery"

    async def local_delivery(self, rcpt_tos, server, session, envelope):
        for to in rcpt_tos:
            logger.info("Local delivery for %s", to)

            try:
                msg = BytesParser(policy=policy.default).parsebytes(envelope.content)
                account = account_manager.get_account_for_address(to)

                await storage.store_mail(
                    account, msg, envelope.mail_from, envelope.rcpt_tos
                )

                # Send push notification to user
                await push.notify_account(
                    account, f"Incomming message from {envelope.mail_from}"
                )

                logger.info("Message delivered to account %s", account.name)
            except:
                import traceback

                traceback.print_exc()
                # import ipdb; ipdb.set_trace()
                await self.save_failed_msg(
                    session, envelope
                )  # TODO handle multiple tos
                print("Error for current message")

            return "250 Message accepted for delivery"


class MxRecord(object):
    """ Ease MX selection """

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
            msg = f"No usable DNS records found: {self.domain}"
            raise ValueError(msg)
        return self._records

    async def _resolve_a(self):
        answer = await self.resolver.query(self.domain, "A")
        expiration = 0
        now = time.time()
        ret = []
        for rdata in answer:
            ret.append((0, self.domain))
            expiration = max(expiration, now + rdata.ttl)
        return ret, expiration

    async def _resolve_mx(self):
        answer = await self.resolver.query(self.domain, "MX")
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
            except DNSError:
                raise


class MsgSender:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

    def group_by_fqdn(self, address):
        """ Group mails by domains """

        result = defaultdict(list)
        for add in address:
            fqdn = add.split("@")[1]
            result[fqdn].append(add)

        return result

    async def send(self, msg, from_addr, to_addrs):
        """ Relay message to other party """

        status = {}
        for addr in to_addrs.items():
            status[addr] = {"status": "NOTDELIVERED", "reason": "NOT_PROCESSED"}

        for fqdn, addresses in self.group_by_fqdn(to_addrs).items():
            try:
                mxs = await MxRecord(fqdn).get()
            except DNSError as e:
                logger.warning("MX for %s not found" % fqdn)
                for addr in addresses:
                    status[addr] = {"status": "ERROR", "reason": "MX_NOT_FOUND"}
                continue

            for _, mx in mxs:
                try_another_mx = False
                try:
                    result = await self._relay_to(mx, from_addr, addresses, msg)

                    # Here result is good for at least one recipient
                    for addr in addresses:
                        addr_status = result.get(addr, ("250", "Delivered"))
                        if addr_status[0].startswith("25"):
                            status[addr] = {
                                "status": "DELIVERED",
                                "smtp_info": addr_status,
                            }
                        else:
                            status[addr] = {
                                "status": "ERROR",
                                "reason": "SMTP_ERROR",
                                "smtp_info": addr_status,
                            }
                except smtplib.SMTPRecipientsRefused as e:
                    # Failed for all recipients
                    for addr in addresses:
                        status[addr] = {
                            "status": "ERROR",
                            "reason": "SMTP_ERROR",
                            "smtp_info": e.recipients[addr],
                        }
                    logger.exception("Fail to send mail")

                except smtplib.SMTPException as e:
                    # Failed for all recipients
                    for addr in addresses:
                        status[addr] = {
                            "status": "ERROR",
                            "reason": "SMTP_ERROR",
                            "smtp_info": str(e),
                        }
                    logger.exception("Fail to send mail")

                except TimeoutError:
                    # Can't connect
                    try_another_mx = True
                    for addr in addresses:
                        status[addr] = {
                            "status": "ERROR",
                            "reason": "MX_TIMEOUT",
                            "smtp_info": "Timeout while trying to access MX",
                        }
                    logger.exception("Timeout error")

                except Exception as e:
                    for addr in addresses:
                        status[addr] = {
                            "status": "ERROR",
                            "reason": "UNKNOWN_ERROR",
                            "smtp_info": f"Unkwnow error: {e}",
                        }
                    logger.exception("Unknown error while sending to %s", mx)

                if not try_another_mx:
                    break

        return status

    async def _relay_to(self, hostname, from_addr, to_addrs, msg):
        logger.info(
            "Try to relay mail to %s from %s to %s", hostname, from_addr, str(to_addrs)
        )
        return await self.loop.run_in_executor(
            None, self._sendmsg, hostname, 25, msg, from_addr, to_addrs
        )

    def _sendmsg(self, host, port, msg, from_addr, to_addrs):
        logger.info("Send mail from %s to %s", from_addr, to_addrs)
        if settings.DEBUG:
            print("Should send...")
            print(msg)
            result = {}
            for addr in to_addrs:
                result[addr] = ("250", "Delivered")
        else:
            with smtplib.SMTP(host=host, port=port) as smtp:
                result = smtp.send_message(msg, from_addr=from_addr, to_addrs=to_addrs)

        return result


async def send_mail(account, msg, from_addr, recipients, loop=None):
    """ Complete process to send an email """
    saved_msg = await storage.store_mail(
        account, msg, from_addr, recipients, incoming=False
    )

    mail_sender = MsgSender(loop=loop)

    # Then we send it
    delivery_status = await mail_sender.send(
        msg, from_addr=from_addr.addr_spec, to_addrs=[a.addr_spec for a in recipients]
    )

    # Then we save status and delivery status
    saved_msg["status"] = "sent"
    saved_msg["delivery_status"] = delivery_status

    await storage.update_mail(account, saved_msg)

    return saved_msg


async def resend_mail(account, msg_to_resend, recipients, loop=None):
    """ Complete process to send an email """

    mail_sender = MsgSender(loop=loop)

    raw_msg = await storage.get_content_msg(msg_to_resend["uid"])

    # We send it
    delivery_status = await mail_sender.send(
        raw_msg,
        from_addr=msg_to_resend["from"].addr_spec,
        to_addrs=[a.addr_spec for a in recipients],
    )

    # Then we save status and delivery status
    msg_to_resend["delivery_status"].update(delivery_status)

    await storage.update_mail(account, msg_to_resend)

    return msg_to_resend
