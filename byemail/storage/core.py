import asyncio
import uuid 
from byemail import mailutils

class Backend():

    def __init__(self, loop=None):
        # Get asyncio loop
        self.loop = loop or asyncio.get_event_loop()

    async def start(self):
        """ Allow backend specific initialisation """
        pass

    async def stop(self):
        """ Allow backend specific tear down code """
        pass

    async def store_bad_msg(self, bad_msg):
        """ To handle msg that failed to parse """
        raise NotImplementedError()

    async def store_content(self, uid, content):
        """ Store raw message content """
        raise NotImplementedError()

    async def get_content_msg(self, uid):
        """ Return EmailMessage instance for this message uid """
        raise NotImplementedError()

    async def get_or_create_mailbox(self, account, address, name):
        """ Create a mailbox """
        raise NotImplementedError()

    async def get_mailboxes(self, account):
        """ Return all mailboxes in db with unread message count and total """
        raise NotImplementedError()

    async def get_mailbox(self, mailbox_id):
        """ Return the selected mailbox """
        raise NotImplementedError()

    async def get_mailbox_mails(self, mailbox_id):
        """ Return the selected mailbox messages """
        raise NotImplementedError()

    async def store_mail(self, account, msg, from_addr, recipients, incoming=True):
        """ Store a mail """
        msg_data = await mailutils.extract_data_from_msg(msg)

        await mailutils.apply_middlewares(msg_data, from_addr, recipients, incoming)

        msg_data['original-sender'] = from_addr
        msg_data['original-recipients'] = recipients

        stored_msg = await self.store_msg(
            msg_data,
            account=account,
            from_addr=from_addr,
            to_addrs=recipients,
            incoming=incoming
        )
        
        print('uid here', stored_msg['uid'], await self.get_mail(stored_msg['uid']))

        await self.store_content(stored_msg['uid'], msg.as_bytes())

        stored_msg['status'] = 'received' if incoming else 'sending'

        await self.update_mail(stored_msg)

        return stored_msg

    async def store_msg(
        self, 
        msg, 
        account, 
        from_addr, 
        to_addrs, 
        incoming=True, 
        extra_data=None, 
        extra_mailbox_message_data=None
    ):
        """ Store message in database """
        raise NotImplementedError()

    async def get_mail(self, mail_uid):
        """ Get message by uid """
        raise NotImplementedError()

    async def get_mail_attachment(self, mail_uid, att_index):
        """ Return a specific mail attachment """
        raise NotImplementedError()

    async def update_mail(self, mail):
        """ Update any mail """
        raise NotImplementedError()

    async def save_user_session(self, session_key, session):
        """ Save modified user session """
        raise NotImplementedError()

    async def get_user_session(self, session_key):
        """ Load user session """
        raise NotImplementedError()

    async def contacts_search(self, account, text):
        """ Search a contact from mailboxes """
        raise NotImplementedError()






