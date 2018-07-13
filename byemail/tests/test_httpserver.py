""" Tests for mailutils module """
import os
import sys
import json
import pytest
import asyncio
from unittest import mock

from . import commons

from byemail.storage import storage

@pytest.fixture
def httpapp(settings):
    from byemail.httpserver import get_app
    return get_app()

def get_auth_cookie(httpapp):
    data = {
        'name': 'test',
        'password': 'test_pass'
    }

    # Authenticate
    _ , response = httpapp.test_client.post('/login', data=json.dumps(data))

    return {'session_key': response.cookies['session_key'].value}

def test_basic(httpapp):
    request, response = httpapp.test_client.get('/')
    assert response.status == 200

def test_auth(httpapp):
    data = {
        'name': 'test',
        'password': 'bad_password'
    }

    request, response = httpapp.test_client.post('/login', data=json.dumps(data))

    assert response.status == 403

    data = {
        'name': 'test',
        'password': 'test_pass'
    }

    request, response = httpapp.test_client.post('/login', data=json.dumps(data))

    assert response.status == 200

def test_send_mail(httpapp):


    data = {
        "recipients":
        [
            {"address":"alt.n2-75zy2uk@yopmail.com","type":"to"}, # test_byemail
            {"address":"alt.n2-75zy2uk@yopmail.com","type":"cc"},
            {"address":"bad@inbox.mailtrap.io","type":"cc"}
        ],
        "subject":"Test mail",
        "content":"Content\nMultiline",
        "attachments":[
            {
                "filename":"testfile.txt",
                "b64":"VGVzdAo="
            }
        ]
    }
    
    cookies = get_auth_cookie(httpapp)
    _ , response = httpapp.test_client.post('/api/sendmail/', data=json.dumps(data), cookies=cookies)

    assert response.status == 200

    assert json.loads(response.body)['delivery_status'] == {
        'alt.n2-75zy2uk@yopmail.com': {'status': 'DELIVERED', 'smtp_info': ['250', 'Delivered']}, 
        'bad@inbox.mailtrap.io': {'reason': 'SMTP_ERROR', 'smtp_info': "(554, b'5.5.1 Error: no inbox for this email')", 'status': 'ERROR'}
    }



def test_contacts_search(loop, httpapp, fake_account):
    """ Test contact search """

    cookies = get_auth_cookie(httpapp)

    request, response = httpapp.test_client.get('/api/contacts/search?text=toto', cookies=cookies)

    assert response.status == 200

    result = json.loads(response.body)

    assert result == []

    loop.run_until_complete(storage.get_or_create_mailbox(fake_account, "titi@localhost", "Titi"))

    request, response = httpapp.test_client.get('/api/contacts/search?text=titi', cookies=cookies)

    assert response.status == 200

    result = json.loads(response.body)

    assert result == ["titi@localhost"]


