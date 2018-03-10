""" Tests for mailutils module """
import os
import pytest
import asyncio
import smtplib
from unittest import mock

from byemail import mta

from . import commons

BASEDIR = os.path.dirname(__file__)
DATADIR = os.path.join(BASEDIR, 'data')


def test_send(loop):

    msend = mta.MailSender(loop)

    msg = commons.get_msg_test()

    from_addr = "test@example.com"
    to_addrs = [
        'spam@pouetpouetpouet.com', 
        'byemail@yopmail.com',
        'other@yopmail.com'
    ]
    
    with mock.patch('byemail.mta.MailSender._relay_to') as smtp_send:

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

    with mock.patch('byemail.mta.MailSender._relay_to') as smtp_send:

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

