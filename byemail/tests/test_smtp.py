""" Tests for mailutils module """
import os
import pytest
import asyncio
import smtplib
from unittest import mock

from byemail import smtp, mailutils
from byemail.account import account_manager
from byemail.storage import storage


from . import commons
from . import conftest

BASEDIR = os.path.dirname(__file__)
DATADIR = os.path.join(BASEDIR, "data")

count = 0


async def fake_send_middleware(msg, from_addr, to_addrs):
    global count
    print("FAKE middleware called")
    count += 1


def test_send(loop, msg_test):

    msend = smtp.MsgSender(loop)

    from_addr = "test@example.com"
    to_addrs = ["spam@pouetpouetpouet.com", "byemail@yopmail.com", "other@yopmail.com"]

    with mock.patch("byemail.smtp.MsgSender._relay_to") as smtp_send:

        f = asyncio.Future(loop=loop)
        f.set_result(
            {
                "byemail@yopmail.com": ("250", "Delivered"),
                "other@yopmail.com": ("534", "Fail for any reason"),
            }
        )
        smtp_send.return_value = f

        result = loop.run_until_complete(msend.send(msg_test, from_addr, to_addrs))

        print(result)

        assert result == {
            "spam@pouetpouetpouet.com": {"status": "ERROR", "reason": "MX_NOT_FOUND"},
            "byemail@yopmail.com": {
                "status": "DELIVERED",
                "smtp_info": ("250", "Delivered"),
            },
            "other@yopmail.com": {
                "status": "ERROR",
                "reason": "SMTP_ERROR",
                "smtp_info": ("534", "Fail for any reason"),
            },
        }

    with mock.patch("byemail.smtp.MsgSender._relay_to") as smtp_send:

        f = asyncio.Future(loop=loop)
        exc = smtplib.SMTPRecipientsRefused(
            {
                "byemail@yopmail.com": ("452", "Requested action not taken"),
                "other@yopmail.com": ("345", "Another reason"),
            }
        )
        f.set_exception(exc)
        smtp_send.return_value = f

        result = loop.run_until_complete(msend.send(msg_test, from_addr, to_addrs))

        print(result)
        assert result == {
            "spam@pouetpouetpouet.com": {"status": "ERROR", "reason": "MX_NOT_FOUND"},
            "byemail@yopmail.com": {
                "status": "ERROR",
                "reason": "SMTP_ERROR",
                "smtp_info": ("452", "Requested action not taken"),
            },
            "other@yopmail.com": {
                "status": "ERROR",
                "reason": "SMTP_ERROR",
                "smtp_info": ("345", "Another reason"),
            },
        }


def test_send_process(loop, msg_test):

    msend = smtp.MsgSender(loop)

    from_addr = "test@example.com"
    to_addrs = ["spam@pouetpouetpouet.com", "byemail@yopmail.com", "other@yopmail.com"]

    with mock.patch("byemail.smtp.MsgSender._relay_to") as smtp_send:

        f = asyncio.Future(loop=loop)
        f.set_result(
            {
                "byemail@yopmail.com": ("250", "Delivered"),
                "other@yopmail.com": ("534", "Fail for any reason"),
            }
        )
        smtp_send.return_value = f

        result = loop.run_until_complete(msend.send(msg_test, from_addr, to_addrs))

        print(result)

        assert result == {
            "spam@pouetpouetpouet.com": {"status": "ERROR", "reason": "MX_NOT_FOUND"},
            "byemail@yopmail.com": {
                "status": "DELIVERED",
                "smtp_info": ("250", "Delivered"),
            },
            "other@yopmail.com": {
                "status": "ERROR",
                "reason": "SMTP_ERROR",
                "smtp_info": ("534", "Fail for any reason"),
            },
        }

    with mock.patch("byemail.smtp.MsgSender._relay_to") as smtp_send:

        f = asyncio.Future(loop=loop)
        exc = smtplib.SMTPRecipientsRefused(
            {
                "byemail@yopmail.com": ("452", "Requested action not taken"),
                "other@yopmail.com": ("345", "Another reason"),
            }
        )
        f.set_exception(exc)
        smtp_send.return_value = f

        result = loop.run_until_complete(msend.send(msg_test, from_addr, to_addrs))

        print(result)
        assert result == {
            "spam@pouetpouetpouet.com": {"status": "ERROR", "reason": "MX_NOT_FOUND"},
            "byemail@yopmail.com": {
                "status": "ERROR",
                "reason": "SMTP_ERROR",
                "smtp_info": ("452", "Requested action not taken"),
            },
            "other@yopmail.com": {
                "status": "ERROR",
                "reason": "SMTP_ERROR",
                "smtp_info": ("345", "Another reason"),
            },
        }


def test_receive(loop):

    msg_handler = smtp.MsgHandler(loop=loop)

    with mock.patch("byemail.smtp.storage") as storage_mock, mock.patch(
        "byemail.account.settings"
    ) as set_mock:

        set_mock.ACCOUNTS = [
            {
                "name": "suzie",
                "password": "crepe",
                "accept": ["@shopping.example.net"],
                "address": "Suzie Q <suzie@shopping.example.net>",
            }
        ]

        # Reload accounts
        account_manager.load_accounts()

        fut = asyncio.Future(loop=loop)
        fut.set_result({})

        storage_mock.store_mail.return_value = fut
        storage_mock.store_bad_msg.return_value = fut

        envelope = commons.objectview(
            dict(
                content=conftest.MAIL_TEST,
                mail_from="joe@football.example.com",
                rcpt_tos=["suzie@shopping.example.net"],
            )
        )

        session = commons.objectview(dict(peer="peer", host_name="hostname"))

        loop.run_until_complete(msg_handler.handle_DATA("127.0.0.1", session, envelope))

        storage_mock.store_mail.assert_called_once()


@pytest.mark.skipif("TRAVIS" in os.environ, reason="Not working on travis")
def test_send_mail(loop, fake_account, msg_test, settings):

    loop.run_until_complete(storage.start())

    from_addr = mailutils.parse_email("test@example.com")
    to_addrs = [mailutils.parse_email("bad@inbox.mailtrap.io")]

    # First with bad recipient
    result = loop.run_until_complete(
        smtp.send_mail(fake_account, msg_test, from_addr, to_addrs)
    )

    print(result)

    assert result["delivery_status"] == {
        "bad@inbox.mailtrap.io": {
            "reason": "SMTP_ERROR",
            "smtp_info": "(554, b'5.5.1 Error: no inbox for this email')",
            "status": "ERROR",
        }
    }

    # Then good recipient
    to_addrs = [mailutils.parse_email("alt.n2-75zy2uk@yopmail.com")]

    result = loop.run_until_complete(
        smtp.send_mail(fake_account, msg_test, from_addr, to_addrs)
    )

    print(result)

    assert result["delivery_status"] == {
        "alt.n2-75zy2uk@yopmail.com": {
            "status": "DELIVERED",
            "smtp_info": ("250", "Delivered"),
        }
    }


def test_resend_mail(loop, fake_account, msg_test, settings):

    loop.run_until_complete(storage.start())

    from_addr = mailutils.parse_email("test@example.com")

    to_addrs = [
        mailutils.parse_email("byemail@yopmail.com"),
        mailutils.parse_email("other@yopmail.com"),
    ]

    with mock.patch("byemail.smtp.MsgSender._relay_to") as smtp_send:
        f = asyncio.Future(loop=loop)
        f.set_result(
            {
                "byemail@yopmail.com": ("250", "Delivered"),
                "other@yopmail.com": ("534", "Fail for any reason"),
            }
        )
        smtp_send.return_value = f

        mail_to_resend = loop.run_until_complete(
            smtp.send_mail(fake_account, msg_test, from_addr, to_addrs)
        )

    assert mail_to_resend["delivery_status"] == {
        "byemail@yopmail.com": {
            "status": "DELIVERED",
            "smtp_info": ("250", "Delivered"),
        },
        "other@yopmail.com": {
            "status": "ERROR",
            "reason": "SMTP_ERROR",
            "smtp_info": ("534", "Fail for any reason"),
        },
    }

    with mock.patch("byemail.smtp.MsgSender._relay_to") as smtp_send:
        f = asyncio.Future(loop=loop)
        f.set_result({})
        smtp_send.return_value = f

        mail_to_resend = loop.run_until_complete(
            smtp.resend_mail(fake_account, mail_to_resend, [to_addrs[1]])
        )

    # Does the delivery status update ?
    assert mail_to_resend["delivery_status"] == {
        "byemail@yopmail.com": {
            "status": "DELIVERED",
            "smtp_info": ("250", "Delivered"),
        },
        "other@yopmail.com": {"status": "DELIVERED", "smtp_info": ("250", "Delivered")},
    }

