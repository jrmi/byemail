
import os
import asyncio
import pytest
import shutil

from copy import deepcopy

from byemail.storage.sqldb import Backend as SQLBackend
from byemail.storage.tinydb import Backend as TinyBackend
from byemail.mailutils import parse_email, extract_data_from_msg

all_backends = [
    {'class': SQLBackend, 'conf': {'uri': "sqlite://:memory:"}},
    {'class': TinyBackend, 'conf': {'datadir': '/tmp/tinydbtest'}}
]

shutil.rmtree('/tmp/tinydbtest', ignore_errors=True)

@pytest.fixture(params=all_backends, ids=['sql', 'tinydb'])
def backend(request, loop):

    b = request.param
    backend = b['class'](**b['conf'], loop=loop)

    loop.run_until_complete(backend.start())
    yield backend
    loop.run_until_complete(backend.stop())


def test_mailbox(loop, fake_account, backend):

    result = loop.run_until_complete(backend.get_mailboxes(account=fake_account))

    previous_len = len(result)

    loop.run_until_complete(backend.get_or_create_mailbox(account=fake_account, address="address", name="name"))
    result = loop.run_until_complete(backend.get_mailboxes(account=fake_account))

    print(result)

    assert (len(result) == (previous_len + 1)), "Bad result count after mailbox creation"

    assert result[0]['account'] == fake_account.name
    assert result[0]['address'] == "address"
    assert result[0]['name'] == "name"

    uid = result[0]['uid']

    result = loop.run_until_complete(backend.get_mailbox(uid))

    assert result['account'] == fake_account.name
    assert result['name'] == "name"


def test_incoming_mail(loop, fake_account, backend, msg_test, fake_emails, settings):
    run = loop.run_until_complete

    from_addr = msg_test['From'].addresses[0]
    to_addrs = [parse_email(fake_emails()), parse_email(fake_emails())]

    #msg = run(extract_data_from_msg(msg_test))

    print(f"From {from_addr}")
    print(f"To {to_addrs}")

    run(backend.store_mail(
        msg=msg_test,
        account=fake_account,
        from_addr=from_addr,
        recipients=to_addrs, 
        incoming=True
    ))
    
    mailboxes = run(backend.get_mailboxes(fake_account))

    delivered_count = 0

    for mailbox in mailboxes:
        mailbox = run(backend.get_mailbox(mailbox['uid']))

        if mailbox['address'] in from_addr.addr_spec:
            delivered_count += 1
            assert len(mailbox['messages']) == 1

            mail = run(backend.get_mail(mailbox['messages'][0]['uid']))
            
            assert mail['from'].addr_spec == from_addr.addr_spec

    assert delivered_count == 1


def _test_get_attachment(loop, fake_account, backend, msg_test_with_attachments, fake_emails, settings):
    run = loop.run_until_complete

    from_addr = msg_test_with_attachments['From'].addresses[0]
    to_addrs = [parse_email(fake_emails())]

    msg = run(extract_data_from_msg(msg_test_with_attachments))

    print(f"From {from_addr}")
    print(f"To {to_addrs}")

    run(backend.store_msg(
        msg=msg,
        account=fake_account,
        from_addr=from_addr,
        to_addrs=to_addrs, 
        incoming=True, 
        extra_data=None
    ))
    
    mailboxes = run(backend.get_mailboxes(fake_account))

    for mailbox in mailboxes:
        mailbox = run(backend.get_mailbox(mailbox['uid']))
        print(f"Mailbox : {mailbox['address']}")

        if mailbox['address'] in from_addr.addr_spec:
            uid = mailbox['messages'][0]['uid']
            print(f"inbox : {mailbox}")

            attachment = run(backend.get_mail_attachment(uid, 0))
            print(f"AAAAAAAA - {attachment}")

            assert attachment == 'att1'

            attachment = run(backend.get_mail_attachment(uid, 1))

            assert attachment == 'att2'
    
    # Add content message and a way to simplify that

    raise Exception()