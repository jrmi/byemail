#!/usr/bin/env python

import asyncio
from random import randint
from faker import Faker

from byemail import storage
from byemail.conf import settings
from byemail import mailutils
from byemail.account import account_manager

async def main():
    settings.init_settings()
    storage.init_storage()
    fake = Faker()

    for account_name, account in account_manager.accounts.items():
        from_addr = account.address
        print(f"Generate messages for {from_addr}...")

        for _ in range(randint(3,5)):
            to_addr = mailutils.parse_email(fake.safe_email())
            for _ in range(randint(3,5)):
                # First message
                subject = fake.sentence(nb_words=5, variable_nb_words=True)
                msg = mailutils.make_msg(
                    subject=subject,
                    content=fake.text(max_nb_chars=200, ext_word_list=None),
                    from_addr=from_addr,
                    tos=[to_addr],
                    ccs=None,
                    attachments=None
                )
                msg_to_store = await mailutils.extract_data_from_msg(msg)
                saved_msg = await storage.storage.store_msg(
                    msg_to_store,
                    account=account,
                    from_addr=from_addr,
                    to_addrs=[to_addr],
                    incoming=False
                )

                # response
                msg = mailutils.make_msg(
                    subject="Re: " + subject,
                    content=fake.text(max_nb_chars=200, ext_word_list=None),
                    from_addr=to_addr,
                    tos=[from_addr],
                    ccs=None,
                    attachments=None
                )

                msg_to_store = await mailutils.extract_data_from_msg(msg)
                saved_msg = await storage.storage.store_msg(
                    msg_to_store,
                    account=account,
                    from_addr=to_addr,
                    to_addrs=[from_addr],
                    incoming=True
                )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())