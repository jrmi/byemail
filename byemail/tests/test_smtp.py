""" Tests for mailutils module """
import os
import pytest
import asyncio
import smtplib
from unittest import mock

from byemail import smtp
from byemail.account import account_manager

from . import commons

BASEDIR = os.path.dirname(__file__)
DATADIR = os.path.join(BASEDIR, 'data')

count = 0

async def fake_send_middleware(msg, from_addr, to_addrs):
    global count
    print("FAKE middleware called")
    count += 1
    
def test_send(loop):

    msend = smtp.MsgSender(loop)

    msg = commons.get_msg_test()

    from_addr = "test@example.com"
    to_addrs = [
        'spam@pouetpouetpouet.com', 
        'byemail@yopmail.com',
        'other@yopmail.com'
    ]
    
    with mock.patch('byemail.smtp.MsgSender._relay_to') as smtp_send:

        f = asyncio.Future(loop=loop)
        f.set_result(
            {
                'byemail@yopmail.com': ('250', 'Delivered'),
                'other@yopmail.com': ('534', 'Fail for any reason')
            },
        )
        smtp_send.return_value = f

        result = loop.run_until_complete(msend.send(msg, from_addr, to_addrs))

        print(result)

        assert result == {
                'spam@pouetpouetpouet.com': {'status': 'ERROR', 'reason': 'MX_NOT_FOUND'}, 
                'byemail@yopmail.com': {'status': 'DELIVERED', 'stmp_info': ('250', 'Delivered')}, 
                'other@yopmail.com': {'status': 'ERROR', 'reason': 'SMTP_ERROR', 'smtp_info': ('534', 'Fail for any reason')}
            }

    with mock.patch('byemail.smtp.MsgSender._relay_to') as smtp_send:

        f = asyncio.Future(loop=loop)
        exc = smtplib.SMTPRecipientsRefused(
            {
                'byemail@yopmail.com': ('452', 'Requested action not taken'),
                'other@yopmail.com': ('345', 'Another reason')
            }
        )
        f.set_exception(exc)
        smtp_send.return_value = f

        result = loop.run_until_complete(msend.send(msg, from_addr, to_addrs))

        print(result)
        assert result == {
            'spam@pouetpouetpouet.com': {'status': 'ERROR', 'reason': 'MX_NOT_FOUND'}, 
            'byemail@yopmail.com': {'status': 'ERROR', 'reason': 'SMTP_ERROR', 'smtp_info': ('452', 'Requested action not taken')}, 
            'other@yopmail.com': {'status': 'ERROR', 'reason': 'SMTP_ERROR', 'smtp_info': ('345', 'Another reason')}
            }


def test_send_middleware(loop):

    msend = smtp.MsgSender(loop)

    msg = commons.get_msg_test()

    from_addr = "test@example.com"
    to_addrs = [
        'spam@pouetpouetpouet.com', 
        'byemail@yopmail.com',
        'other@yopmail.com'
    ]
    
    with mock.patch('byemail.smtp.MsgSender._relay_to') as smtp_send, \
        mock.patch('byemail.smtp.settings') as set_mock:

        set_mock.OUTGOING_MIDDLEWARES = [
            'byemail.tests.test_smtp.fake_send_middleware',
            'another.bad.middleware'
        ]

        f = asyncio.Future(loop=loop)
        f.set_result(
            {
                'byemail@yopmail.com': ('250', 'Delivered'),
                'other@yopmail.com': ('534', 'Fail for any reason')
            },
        )
        smtp_send.return_value = f

        with pytest.raises(ModuleNotFoundError):
            loop.run_until_complete(msend.send(msg, from_addr, to_addrs))

        assert count == 1


def test_receive(loop):
    msg_handler = smtp.MsgHandler(loop=loop)

    with mock.patch('byemail.smtp.storage') as storage_mock, \
        mock.patch('byemail.account.settings') as set_mock:

        set_mock.ACCOUNTS = [
            {
                'name': 'suzie',
                'password': 'crepe',
                'accept': ['@shopping.example.net'],
                'address': 'Suzie Q <suzie@shopping.example.net>'
            }
        ]
        
        # Reload accounts
        account_manager.load_accounts()

        fut = asyncio.Future(loop=loop)
        fut.set_result({})

        storage_mock.store_msg.return_value = fut
        storage_mock.store_bad_msg.return_value = fut

        envelope = commons.objectview(dict(
            content=commons.MAIL_TEST,
            mail_from="joe@football.example.com",
            rcpt_tos=["suzie@shopping.example.net"]
        ))

        session = commons.objectview(dict(
            peer="peer",
            host_name="hostname"
        ))

        loop.run_until_complete(msg_handler.handle_DATA('127.0.0.1', session, envelope))

        storage_mock.store_msg.assert_called_once()
