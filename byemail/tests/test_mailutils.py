""" Tests for mailutils module """
import os
import pytest
import asyncio
from unittest import mock

from byemail import mailutils

BASEDIR = os.path.dirname(__file__)
DATADIR = os.path.join(BASEDIR, 'data')

DNS_DKIM_RESPONSE_TPL = """v=DKIM1; k=rsa; s=email; p={}"""

message_content = """Hi.

We lost the game.  Are you hungry yet?

Joe."""


def test_make_msg(loop):
    """ Test message composition """
    from_address = mailutils.parse_email("Joe SixPack <joe@football.example.com>")
    to_address = mailutils.parse_email("Suzie Q <suzie@shopping.example.net>")

    with mock.patch('byemail.mailutils.settings') as set_mock:
        set_mock.DKIM_CONFIG = {
            'private_key': os.path.join(DATADIR, 'example_private.pem'),
            'public_key': os.path.join(DATADIR, 'example_public.pem'),
            'selector': 'test',
            'domain': 'example.com',
            'headers': ['From', 'To', 'Subject', 'Date', 'Message-Id']
        }

        msg = mailutils.make_msg(
            "Is dinner ready?",
            message_content,
            from_addr=from_address,
            tos=to_address
        )

        print(msg)

        assert msg['From'] == str(from_address)


def test_extract_data(loop, msg_test):
    """ Test mail extraction data """

    data = loop.run_until_complete(mailutils.extract_data_from_msg(msg_test))

    assert data['from'].addr_spec == "joe@football.example.com"


'''def _test_msg_signing():
    # Use https://www.mail-tester.com to test
    from_address = mailutils.parse_email("Joe SixPack <joe@football.example.com>")
    to_address = mailutils.parse_email("Suzie Q <suzie@shopping.example.net>")

    with mock.patch('byemail.mailutils.settings') as set_mock:
        set_mock.DKIM_CONFIG = {
            'private_key': os.path.join(DATADIR, 'example_private.pem'),
            'public_key': os.path.join(DATADIR, 'example_public.pem'),
            'selector': 'test',
            'domain': 'example.com',
            'headers': ['From', 'To', 'Subject', 'Date', 'Message-Id']
        }

        msg = mailutils.make_msg(
            "Is dinner ready?",
            message_content,
            from_addr=from_address,
            tos=to_address
        )

        dkim_sign = mailutils.gen_dkim_sign(msg)

        #new_dkim = mailutils.gen_dkim_sign2(msg)
        #assert old_dkim == new_dkim, "DKIM differs"

        msg['DKIM-Signature'] = dkim_sign
        print(msg['DKIM-Signature'])


    with open(os.path.join(DATADIR, 'example_public.pem')) as key:
        publickey = key.read().replace('\n', '')\
            .replace('-----BEGIN PUBLIC KEY-----', '')\
            .replace('-----END PUBLIC KEY-----', '')

    def dnsfunc(*args):
        print("Called with ", *args)
        return DNS_DKIM_RESPONSE_TPL.format(publickey)

    assert dkim.verify(msg.as_string().encode(), dnsfunc=dnsfunc)'''


