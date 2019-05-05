import os
import asyncio
import pytest
import shutil
import datetime
import base64

from copy import deepcopy

from byemail.storage.sqldb import Backend as SQLBackend
from byemail.storage.tinydb import Backend as TinyBackend
from byemail import storage
from byemail.mailutils import parse_email, extract_data_from_msg

all_backends = [
    {
        "class": SQLBackend,
        "conf": {
            "config": {
                "default": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {"file_path": ":memory:"},
                }
            }
        },
    },
    {"class": TinyBackend, "conf": {"datadir": "/tmp/tinydbtest"}},
]

shutil.rmtree("/tmp/tinydbtest", ignore_errors=True)


@pytest.fixture(params=all_backends, ids=["sql", "tinydb"])
def backend(request, loop):

    b = request.param
    backend = b["class"](**b["conf"], loop=loop)

    loop.run_until_complete(backend.start())
    yield backend
    loop.run_until_complete(backend.stop())


def test_mailbox(loop, fake_account, other_fake_account, backend):

    result = loop.run_until_complete(backend.get_mailboxes(account=fake_account))

    previous_len = len(result)

    loop.run_until_complete(
        backend.get_or_create_mailbox(
            account=fake_account, address="address", name="name"
        )
    )
    result = loop.run_until_complete(backend.get_mailboxes(account=fake_account))

    print(result)

    assert len(result) == (previous_len + 1), "Bad result count after mailbox creation"

    assert result[0]["account"] == fake_account.name
    assert result[0]["address"] == "address"
    assert result[0]["name"] == "name"

    uid = result[0]["uid"]

    result = loop.run_until_complete(backend.get_mailbox(fake_account, uid))

    assert result["account"] == fake_account.name
    assert result["name"] == "name"

    # Check security
    with pytest.raises(storage.DoesntExists):
        result = loop.run_until_complete(backend.get_mailbox(other_fake_account, uid))


def test_incoming_mail(
    loop, fake_account, other_fake_account, backend, msg_test, fake_emails, settings
):
    run = loop.run_until_complete

    from_addr = msg_test["From"].addresses[0]
    to_addrs = [parse_email(fake_emails()), parse_email(fake_emails())]

    print(f"From {from_addr}")
    print(f"To {to_addrs}")

    run(
        backend.store_mail(
            msg=msg_test,
            account=fake_account,
            from_addr=from_addr,
            recipients=to_addrs,
            incoming=True,
        )
    )

    mailboxes = run(backend.get_mailboxes(fake_account))

    delivered_count = 0

    for mailbox in mailboxes:
        mailbox = run(backend.get_mailbox(fake_account, mailbox["uid"]))

        if mailbox["address"] in from_addr.addr_spec:
            # Count message to be sure at least one have been recorded
            delivered_count += 1

            # Check mail
            mail = run(backend.get_mail(fake_account, mailbox["messages"][0]["uid"]))
            assert mail["from"].addr_spec == from_addr.addr_spec
            assert mail["status"] == "received"

            # Check mailbox data
            assert len(mailbox["messages"]) == 1
            assert mailbox["total"] == 1
            assert mailbox["last_message"] == mail["date"]

            unreads = run(backend.get_unreads(fake_account))

            assert len(unreads) == 1

            assert unreads == [
                {"mailbox": mailbox["uid"], "message": mailbox["messages"][0]["uid"]}
            ]

            # Check security
            with pytest.raises(storage.DoesntExists):
                mail = run(
                    backend.get_mail(other_fake_account, mailbox["messages"][0]["uid"])
                )

    assert delivered_count == 1


def test_get_attachment(
    loop,
    fake_account,
    other_fake_account,
    backend,
    msg_test_with_attachments,
    fake_emails,
    settings,
):
    run = loop.run_until_complete

    del msg_test_with_attachments["From"]

    msg_test_with_attachments["From"] = "test@bar.foo"

    from_addr = msg_test_with_attachments["From"].addresses[0]
    to_addrs = [parse_email(fake_emails())]

    out_mail = run(
        backend.store_mail(
            msg=msg_test_with_attachments,
            account=fake_account,
            from_addr=from_addr,
            recipients=to_addrs,
            incoming=True,
        )
    )

    print("out mail", out_mail)

    mailboxes = run(backend.get_mailboxes(fake_account))

    for mailbox in mailboxes:
        mailbox = run(backend.get_mailbox(fake_account, mailbox["uid"]))

        if mailbox["address"] in from_addr.addr_spec:
            uid = mailbox["messages"][0]["uid"]

            attachment = run(backend.get_mail_attachment(fake_account, uid, 0))
            assert attachment == (
                {
                    "content-id": None,
                    "filename": "att1.txt",
                    "index": 0,
                    "type": "text/plain",
                },
                "att1\n",
            )

            attachment = run(backend.get_mail_attachment(fake_account, uid, 1))
            assert attachment == (
                {
                    "content-id": None,
                    "filename": "att2.txt",
                    "index": 1,
                    "type": "text/plain",
                },
                "att2\n",
            )

            # Check security
            with pytest.raises(storage.DoesntExists):
                attachment = run(
                    backend.get_mail_attachment(other_fake_account, uid, 1)
                )


def test_read_mail(
    loop, fake_account, other_fake_account, backend, msg_test, fake_emails, settings
):
    run = loop.run_until_complete

    from_addr = msg_test["From"].addresses[0]
    to_addrs = [parse_email(fake_emails()), parse_email(fake_emails())]

    print(f"From {from_addr}")
    print(f"To {to_addrs}")

    run(
        backend.store_mail(
            msg=msg_test,
            account=fake_account,
            from_addr=from_addr,
            recipients=to_addrs,
            incoming=True,
        )
    )

    mailboxes = run(backend.get_mailboxes(fake_account))

    for mailbox in mailboxes:
        mailbox = run(backend.get_mailbox(fake_account, mailbox["uid"]))

        if mailbox["address"] in from_addr.addr_spec:

            msg_uid = mailbox["messages"][0]["uid"]

            unreads = run(backend.get_unreads(fake_account))

            assert len(unreads) >= 1

            assert {"mailbox": mailbox["uid"], "message": msg_uid} in unreads

            run(backend.mark_mail_read(fake_account, msg_uid))

            unreads = run(backend.get_unreads(fake_account))

            assert {"mailbox": mailbox["uid"], "message": msg_uid} not in unreads


def test_session(loop, fake_account, backend):
    """ Test session in storage """
    run = loop.run_until_complete

    session_key = "testsessionkey"

    session = {"fakedict": "fakevalue"}

    run(backend.save_user_session(session_key, session))

    session_from_storage = run(backend.get_user_session(session_key))

    assert "fakedict" in session_from_storage
    assert session_from_storage["fakedict"] == "fakevalue"

    session_from_storage["newvalue"] = 42
    session_from_storage["fakedict"] = "badvalue"

    run(backend.save_user_session(session_key, session_from_storage))

    session_from_storage = run(backend.get_user_session(session_key))

    assert "fakedict" in session_from_storage
    assert "newvalue" in session_from_storage
    assert session_from_storage["fakedict"] == "badvalue"
    assert session_from_storage["newvalue"] == 42


def test_search_contact(loop, fake_account, backend, msg_test, fake_emails, settings):
    """ Test contact search feature """
    run = loop.run_until_complete

    from_addr = msg_test["From"].addresses[0]
    to_addrs = [parse_email(fake_emails()), parse_email(fake_emails())]

    run(
        backend.store_mail(
            msg=msg_test,
            account=fake_account,
            from_addr=from_addr,
            recipients=to_addrs,
            incoming=True,
        )
    )

    search = run(backend.contacts_search(fake_account, "foot"))

    assert len(search) == 1
    assert search[0] == "joe@football.example.com"


def test_store_bad_msg(loop, fake_account, backend, msg_test, fake_emails, settings):
    """ Test contact search feature """
    run = loop.run_until_complete

    from_addr = msg_test["From"].addresses[0]
    to_addrs = [parse_email(fake_emails()), parse_email(fake_emails())]

    to_save = {
        "status": "error",
        "peer": "fake@peer.old",
        "host_name": "fake@hostname.old",
        "from": from_addr,
        "tos": to_addrs,
        "subject": msg_test["Subject"],
        "received": datetime.datetime.now().isoformat(),
        "data": base64.b64encode(msg_test.as_bytes()).decode("utf-8"),
    }

    run(backend.store_bad_msg(to_save))

