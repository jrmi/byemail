import email
import datetime

import arrow

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer, SerializationMiddleware

local_db = None

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

async def get(filter):
    results = local_db.search(filter)
    if len(results) < 1:
        raise DoesntExists()
    if len(results) > 1:
        raise MultipleResults()
    return results[0]

async def get_or_create(filter, default):
    try:
        result = await get(filter)
        return result
    except DoesntExists:
        local_db.insert(default)
        return default


async def get_db():
    global local_db
    if local_db is None:
        serialization = SerializationMiddleware()
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
        serialization.register_serializer(AddressSerializer(), 'TinyAddress')

        local_db = TinyDB('db.json', storage=serialization)

    return local_db

async def get_mailboxes():
    mailboxes = list(local_db.search(Mailbox.type=='mailbox'))

    sorted_mailboxes = sorted(mailboxes, key=lambda x: x['last_message'], reverse=True)
    
    for mailbox in sorted_mailboxes:
        #print('Mailbox for %s - last message: %s (#%d messages)' % (mailbox['from'], mailbox['last_message'], len(mailbox['messages'])))
        sorted_messages = sorted(mailbox['messages'], key=lambda x : x['date'], reverse=True)
        for msg in sorted_messages:
            message = db.search( (Mailbox.type == 'mail') & (Mailbox.status == 'delivered') & (Mailbox['id'] == msg['id']) )[0]
            #print('    ', message['date'], message['subject'] )
        #print('-')