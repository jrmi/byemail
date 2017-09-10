import email
import datetime
import asyncio
import base64
import uuid

from email import policy
from email.parser import BytesParser

import arrow

from tinydb import TinyDB, Query
from tinydb_serialization import Serializer, SerializationMiddleware


class DoesntExists(Exception):
    pass

class MultipleResults(Exception):
    pass

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime.datetime  # The class this serializer handles

    def encode(self, obj):
        return arrow.get(obj).for_json()

    def decode(self, s):
        return arrow.get(s).datetime

class AddressSerializer(Serializer):
    OBJ_CLASS = email.headerregistry.Address  # The class this serializer handles

    def encode(self, obj):
        return "(_|_)".join([obj.addr_spec, obj.display_name])

    def decode(self, s):
        addr_spec, display_name = s.split('(_|_)')

        return email.headerregistry.Address(display_name=display_name, addr_spec=addr_spec)

class DbBackend():
    def __init__(self):
        super().__init__()

        loop = asyncio.get_event_loop()

        serialization = SerializationMiddleware()
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
        serialization.register_serializer(AddressSerializer(), 'TinyAddress')

        self.db = TinyDB('db.json', storage=serialization)
        self.maildb = TinyDB('maildb.json')

    async def get(self, filter):
        results = self.db.search(filter)
        if len(results) < 1:
            raise DoesntExists()
        if len(results) > 1:
            raise MultipleResults()
        return results[0]

    async def get_or_create(self, filter, default):
        try:
            result = await self.get(filter)
            return result
        except DoesntExists:
            self.db.insert(default)
            return default

    async def store_bad_msg(self, bad_msg):
        """ To handle msg that failed to parse """

        self.db.insert(bad_msg)

    async def store_content(self, uid, content):
        """ Store raw content """
        b64_content = base64.b64encode(content).decode('utf-8'),
        return self.maildb.insert({'uid': uid, 'content': b64_content})

    async def get_content_msg(self, uid):
        """ Return EmailMessage instance for this message uid """
        Mail = Query()

        results = self.maildb.search(Mail.uid == uid)
        if len(results) < 1:
            raise DoesntExists()
        if len(results) > 1:
            raise MultipleResults()
        b64_content = results[0]['content']

        msg = BytesParser(policy=policy.default).parsebytes(base64.b64decode(b64_content))

        return msg

    async def store_msg(self, msg):
        """ Store message """
        # First define uid
        msg['uid'] = uuid.uuid4().hex

        # Then save data in maildb
        await self.store_content(msg['uid'], msg['content'])

        del(msg['content'])


        eid = self.db.insert(msg)

        Mailbox = Query()
        msg_from = msg['from'].addr_spec

        # Get mailbox if exists or create it
        mailbox = await self.get_or_create((Mailbox.type == 'mailbox') & (Mailbox['from'] == msg_from), {
            'uid': uuid.uuid4().hex,
            'type': 'mailbox',
            'from': msg_from,
            'display_name': msg['from'].display_name,
            'last_message': msg['date'],
            'messages': [],
        })

        # Update last_message date
        if mailbox['last_message'] < msg ['date']:
            mailbox['last_message'] = msg['date']

        mailbox['messages'].append({
            'id': eid,
            'uid': msg['uid'],
            'date': msg['date'],
            'subject': msg['subject'],
            'attachment_count': len(msg['attachments'])
        })

        mailbox['messages'] = sorted(mailbox['messages'], key=lambda x: x['date'], reverse=True)

        self.db.update(mailbox, (Mailbox.type == 'mailbox') & (Mailbox['from'] == msg_from))

    async def get_mailboxes(self):
        Mailbox = Query()

        mailboxes = list(self.db.search(Mailbox.type=='mailbox'))
        sorted_mailboxes = sorted(mailboxes, key=lambda x: x['last_message'], reverse=True)

        return sorted_mailboxes

    async def get_mailbox(self, mailbox_id):
        Mailbox = Query()
        mailbox = await self.get(Mailbox.uid==mailbox_id)

        return mailbox

    async def get_mail(self, mail_uid):
        Message = Query()

        mail = await self.get(Message.uid==mail_uid)

        return mail


storage = DbBackend()
