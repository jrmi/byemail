""" Tests for mailutils module """
import os
import sys
import json
import pytest
import asyncio
import smtplib
from unittest import mock

from byemail.conf import settings

from . import commons
from icecream import ic

@pytest.fixture
def httpapp():
    # Override settings before
    os.environ['BYEMAIL_SETTINGS_MODULE'] = 'byemail.tests.workdir.settings'

    settings.init_settings()
    
    from byemail.httpserver import get_app
    return get_app()

@pytest.fixture
def auth_app():
    pass


def test_basic(httpapp):
    request, response = httpapp.test_client.get('/')
    assert response.status == 200

def test_auth(httpapp):
    data = {''}

    data = {
        'name': 'test',
        'password': 'test_pass'
    }

    request, response = httpapp.test_client.post('/login', data=json.dumps(data))

    assert response.status == 200
