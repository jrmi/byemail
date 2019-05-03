""" Tests for mailutils module """
import os
import sys
import json
import pytest
import asyncio
from unittest import mock
from sanic.websocket import WebSocketProtocol

from . import commons

from byemail.storage import storage

BASEDIR = os.path.dirname(__file__)
WORKDIR = os.path.join(BASEDIR, "workdir")


@pytest.fixture
def httpapp(loop, settings):
    from byemail.httpserver import get_app

    storage.loop = loop
    loop.run_until_complete(storage.start())

    return get_app()


@pytest.fixture
def test_cli(loop, sanic_client, settings):
    from byemail.httpserver import get_app

    storage.loop = loop
    loop.run_until_complete(storage.start())

    return loop.run_until_complete(sanic_client(get_app(), protocol=WebSocketProtocol))


def get_auth_cookie(loop, test_client):
    data = {"name": "test", "password": "test_pass"}

    # Authenticate
    response = loop.run_until_complete(
        test_client.post("/login", data=json.dumps(data))
    )

    return {"session_key": response.cookies["session_key"].value}


def test_basic(loop, test_cli):
    response = loop.run_until_complete(test_cli.get("/"))
    assert response.status == 200


def test_auth(loop, test_cli):
    data = {"name": "test", "password": "bad_password"}

    response = loop.run_until_complete(test_cli.post("/login", data=json.dumps(data)))

    assert response.status == 403

    data = {"name": "test", "password": "test_pass"}

    response = loop.run_until_complete(test_cli.post("/login", data=json.dumps(data)))

    assert response.status == 200


def test_send_mail(loop, test_cli):

    data = {
        "recipients": [
            {"address": "alt.n2-75zy2uk@yopmail.com", "type": "to"},  #  test_byemail
            {"address": "alt.n2-75zy2uk@yopmail.com", "type": "cc"},
            {"address": "bad@inbox.mailtrap.io", "type": "cc"},
        ],
        "subject": "Test mail",
        "content": "Content\nMultiline",
        "attachments": [{"filename": "testfile.txt", "b64": "VGVzdAo="}],
    }

    cookies = get_auth_cookie(loop, test_cli)
    response = loop.run_until_complete(
        test_cli.post(
            f"/api/users/test/sendmail/", data=json.dumps(data), cookies=cookies
        )
    )

    assert response.status == 200

    result = loop.run_until_complete(response.json())

    assert result["delivery_status"] == {
        "alt.n2-75zy2uk@yopmail.com": {
            "status": "DELIVERED",
            "smtp_info": ["250", "Delivered"],
        },
        "bad@inbox.mailtrap.io": {
            "reason": "SMTP_ERROR",
            "smtp_info": "(554, b'5.5.1 Error: no inbox for this email')",
            "status": "ERROR",
        },
    }


def test_contacts_search(loop, test_cli, fake_account):
    """ Test contact search """

    cookies = get_auth_cookie(loop, test_cli)

    response = loop.run_until_complete(
        test_cli.get("/api/users/test/contacts/search?text=toto", cookies=cookies)
    )

    assert response.status == 200

    result = loop.run_until_complete(response.json())

    assert result == []

    loop.run_until_complete(
        storage.get_or_create_mailbox(fake_account, "titi@localhost", "Titi")
    )

    response = loop.run_until_complete(
        test_cli.get("/api/users/test/contacts/search?text=titi", cookies=cookies)
    )

    assert response.status == 200

    result = loop.run_until_complete(response.json())

    assert result == ["titi@localhost"]

