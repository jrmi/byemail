from email import policy
from email.parser import BytesParser
from byemail.mailutils import parse_email

from byemail.account import account_manager

INCOMING_1 = (
    b"""Content-Type: text/plain; charset="utf-8"\r
Content-Transfer-Encoding: 7bit\r
MIME-Version: 1.0\r
From: Suzie <suzie@example.com>\r
Subject: First mail\r
Message-Id: <152060134529.22888.2561159661807344297@emiter>\r
To: Test <test@example.net>\r
Date: Fri, 09 Mar 2019 14:15:45 +0100\r
\r
Do you read me?\r
\r
Suzie.\r
\r
""",
    "Suzie <suzie@example.com>",
)

INCOMING_2 = (
    b"""Content-Type: text/plain; charset="utf-8"\r
Content-Transfer-Encoding: 7bit\r
MIME-Version: 1.0\r
From: Sam <sam@example.com>\r
Subject: My mail\r
Message-Id: <152060134529.22888.2561159661807344297@emiter>\r
To: Test <test@example.net>\r
Date: Fri, 09 Mar 2019 14:15:45 +0100\r
\r
Do you read me?\r
\r
Sam.\r
\r
""",
    "Sam <sam@example.com>",
)

OUTGOING_1 = (
    b"""Content-Type: text/plain; charset="utf-8"\r
Content-Transfer-Encoding: 7bit\r
MIME-Version: 1.0\r
From: Test <test@example.com>\r
Subject: Second mail\r
Message-Id: <152060134529.22888.2561159661807344298@emiter>\r
To: Suzie <suzie@example.com>\r
Date: Fri, 09 Mar 2019 14:16:45 +0100\r
\r
Yes sure, why not.\r
\r
Test.\r
\r
""",
    [parse_email("Suzie <suzie@example.com>")],
)

incoming_messages = [INCOMING_1, INCOMING_2]
outgoing_messages = [OUTGOING_1]


async def populate_with_test_data(storage):
    """ Populate database with test data for testing purpose """

    account = account_manager.get_account_for_address("test@example.com")
    print(account)

    for msg_src, from_addr in incoming_messages:
        msg = BytesParser(policy=policy.default).parsebytes(msg_src)
        recipients = [parse_email("Test <test@example.com>")]
        await storage.store_mail(account, msg, from_addr, recipients, incoming=True)

    for msg_src, recipients in outgoing_messages:
        from_addr = "test@example.com"
        msg = BytesParser(policy=policy.default).parsebytes(msg_src)
        await storage.store_mail(account, msg, from_addr, recipients, incoming=False)
