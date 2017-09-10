import email
import datetime
import asyncio

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

    async def store_msg(self, msg):
        """ Store message """
        eid = self.db.insert(msg)

        Mailbox = Query()
        msg_from = msg['from'].addr_spec

        # Get mailbox if exists
        mailbox = await self.get_or_create((Mailbox.type == 'mailbox') & (Mailbox['from'] == msg_from), {
            'type': 'mailbox',
            'from': msg_from,
            'last_message': msg['date'],
            'messages': [],
        })

        # Update last_message date
        if mailbox['last_message'] < msg ['date']:
            mailbox['last_message'] = msg['date']

        mailbox['messages'].append({
            'id': eid,
            'date': msg['date'],
            'subject': msg['subject']
        })

        self.db.update(mailbox, (Mailbox.type == 'mailbox') & (Mailbox['from'] == msg_from))


    async def get_mailboxes(self):
        Mailbox = Query()

        mailboxes = list(self.db.search(Mailbox.type=='mailbox'))

        sorted_mailboxes = sorted(mailboxes, key=lambda x: x['last_message'], reverse=True)

        for mailbox in sorted_mailboxes:
            mailbox['eid'] = mailbox.eid

            '''mailbox['messages'] = []
            for msg in sorted_messages:
                if 'id' in msg: # Hack to avoid strange fail on second query
                    mailbox['messages'].append(self.db.get(eid=msg['id']))'''

        return sorted_mailboxes

    async def get_mailbox(self, mailbox_eid):
        Mailbox = Query()

        mailbox = self.db.get(eid=mailbox_eid)
        mailbox['id'] = mailbox.eid

        sorted_messages = sorted(mailbox['messages'], key=lambda x: x['date'], reverse=True)
        mailbox['messages'] = []
        for msg in sorted_messages:
            if 'id' in msg: # Hack to avoid strange fail on second query
                msg = self.db.get(eid=msg['id'])
                msg['id'] = msg.eid
                del(msg['data'])
                mailbox['messages'].append(msg)

        return mailbox

    async def get_mail(self, mail_eid):
        Mailbox = Query()

        mail = self.db.get(eid=mail_eid)
        mail['id'] = mail.eid

        # parse mail content

        return mail


storage = DbBackend()
