import os
import asyncio

import pytest

from faker import Faker

from email.headerregistry import AddressHeader, HeaderRegistry

fake = Faker()
fake.seed(42)


MAIL_TEST = b"""Content-Type: text/plain; charset="utf-8"\r
Content-Transfer-Encoding: 7bit\r
MIME-Version: 1.0\r
From: Joe SixPack <joe@football.example.com>\r
Subject: Is dinner ready?\r
Message-Id: <152060134529.22888.2561159661807344297@emiter>\r
To: Suzie Q <suzie@shopping.example.net>\r
To: Roger M <roger@shopping.example.com>\r
Date: Fri, 09 Mar 2017 14:15:45 +0100\r
\r
Hi.\r
\r
We lost the game.  Are you hungry yet?\r
\r
Joe.\r
\r
"""

# @pytest.fixture(scope="session")
# def loop():
#    asyncio.set_event_loop(None)
#    return


@pytest.yield_fixture(scope="session")
def loop():
    asyncio.set_event_loop(None)
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def msg_test():
    from email import policy
    from email.parser import BytesParser

    header_registry = HeaderRegistry()
    header_registry.map_to_type("To", AddressHeader)
    policy = policy.EmailPolicy(header_factory=header_registry)

    return BytesParser(policy=policy).parsebytes(MAIL_TEST)


@pytest.fixture
def msg_test_with_attachments(msg_test):
    for content in ["att1", "att2"]:
        print(msg_test)
        msg_test.add_attachment(content, subtype="plain", filename=f"{content}.txt")
    return msg_test


@pytest.fixture
def fake_account():
    from byemail.account import Account

    return Account(1, "test", "test", "test@example.com", "test@example.com")


@pytest.fixture
def other_fake_account():
    from byemail.account import Account

    return Account(1, "test2", "test2", "test2@example.com", "test2@example.com")


@pytest.fixture
def fake_emails():
    return fake.email


@pytest.fixture(scope="session")
def settings():
    from byemail.conf import settings

    # Override settings before
    os.environ["BYEMAIL_SETTINGS_MODULE"] = "byemail.tests.workdir.settings"

    settings.init_settings()

    return settings
