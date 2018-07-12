""" Tests for mailutils module """
import os
import sys
import json
import pytest
import asyncio
from unittest import mock

from . import commons

@pytest.fixture
def httpapp(settings):
    from byemail.httpserver import get_app
    return get_app()

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
        'name': 'test',
        'password': 'test_pass'
    }

    # Authenticate
    request, response = httpapp.test_client.post('/login', data=json.dumps(data))

    assert response.status == 200

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
    cookies = {'session_key': response.cookies['session_key'].value}
    request, response = httpapp.test_client.post('/api/sendmail/', data=json.dumps(data), cookies=cookies)

    assert response.status == 200

    assert json.loads(response.body)['delivery_status'] == {
        'alt.n2-75zy2uk@yopmail.com': {'status': 'DELIVERED', 'stmp_info': ['250', 'Delivered']}, 
        'bad@inbox.mailtrap.io': {'reason': 'SMTP_ERROR', 'smtp_info': "(554, b'5.5.1 Error: no inbox for this email')", 'status': 'ERROR'}
    }
