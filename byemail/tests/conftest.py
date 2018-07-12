import os
import asyncio

import pytest

MAIL_TEST = b"""Content-Type: text/plain; charset="utf-8"\r
Content-Transfer-Encoding: 7bit\r
MIME-Version: 1.0\r
From: Joe SixPack <joe@football.example.com>\r
Subject: Is dinner ready?\r
Message-Id: <152060134529.22888.2561159661807344297@emiter>\r
To: Suzie Q <suzie@shopping.example.net>\r
Date: Fri, 09 Mar 2017 14:15:45 +0100\r
\r
Hi.\r
\r
We lost the game.  Are you hungry yet?\r
\r
Joe.\r
\r
"""

@pytest.fixture(scope="session")
def loop():
    asyncio.set_event_loop(None)
    return asyncio.new_event_loop()

@pytest.fixture
def msg_test():
    from email import policy
    from email.parser import BytesParser
    return BytesParser(policy=policy.default).parsebytes(MAIL_TEST)

@pytest.fixture
def fake_account():
    from byemail.account import Account
    return Account(1, 'test', 'test', 'test@example.com', 'test@example.com')

@pytest.fixture(scope="session")
def settings():
    from byemail.conf import settings
    
    # Override settings before
    os.environ['BYEMAIL_SETTINGS_MODULE'] = 'byemail.tests.workdir.settings'

    settings.init_settings()

    return settings