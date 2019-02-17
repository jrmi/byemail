import os
import uuid
import base64
import datetime
import asyncio

from email import policy
from email.parser import BytesParser
from email.headerregistry import Address
from email.errors import InvalidHeaderDefect

import arrow

from tinydb import TinyDB, Query
from tinydb_serialization import Serializer, SerializationMiddleware

from byemail import mailutils
from byemail.conf import settings
from byemail.storage import core, DoesntExists, MultipleResults


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime.datetime  # The class this serializer handles

    def encode(self, obj):
        return arrow.get(obj).for_json()

    def decode(self, s):
        return arrow.get(s).datetime

class AddressSerializer(Serializer):
    OBJ_CLASS = Address  # The class this serializer handles

    def encode(self, obj):
        return "(_|_)".join([obj.addr_spec, obj.display_name])

    def decode(self, s):
        addr_spec, display_name = s.split('(_|_)')
        try:
            return Address(display_name=display_name, addr_spec=addr_spec)
        except InvalidHeaderDefect:
            return "not decoded %s" % s

class Backend(core.Backend):
    def __init__(self, datadir="data/", **kwargs):
        super().__init__(**kwargs)

        # Post init_settings things
        if not os.path.isdir(datadir):
            os.makedirs(datadir)

        # TODO put this in start()
        serialization = SerializationMiddleware()
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
        serialization.register_serializer(AddressSerializer(), 'TinyAddress')

        self.db = TinyDB(os.path.join(datadir, 'db.json'), storage=serialization)
        self.maildb = TinyDB(os.path.join(datadir, 'maildb.json'))

    async def get(self, filter):
        """ Helper to get an item by filter """
        results = self.db.search(filter)
        if len(results) < 1:
            raise DoesntExists()
        if len(results) > 1:
            raise MultipleResults()
        return results[0]

    async def get_or_create(self, filter, default):
        """ Helper to get or create an item by filter with default value """
        try:
            result = await self.get(filter)
            return result
        except DoesntExists:
            self.db.insert(default)
            return default

    async def store_bad_msg(self, bad_msg):
        """ To handle msg that failed to parse """
        bad_msg['type'] = 'mail'

        self.db.insert(bad_msg)

    async def store_content(self, uid, content):
        """ Store raw message content """
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
        b64_content = results[0]['content'][0]

        msg = BytesParser(policy=policy.default).parsebytes(base64.b64decode(b64_content))

        return msg

    async def get_or_create_mailbox(self, account, address, name):
        """ Create a mailbox """

        Mailbox = Query()

        mailbox = await self.get_or_create(
            (Mailbox.type == 'mailbox') &
            (Mailbox['address'] == address) &
            (Mailbox['account'] == account.name), {
                'uid': uuid.uuid4().hex,
                'account': account.name,
                'type': 'mailbox',
                'address': address,
                'name': name,
                'last_message': None,
                'messages': [],
            }
        )
        return mailbox

    async def store_msg(self, msg, account, from_addr, to_addrs, incoming=True, extra_data=None):
        """ Store message in database """

        msg['type'] = 'mail'
        
        msg['uid'] = uuid.uuid4().hex

        msg['incoming'] = incoming
        msg['unread'] = incoming
        msg['account'] = account.name

        if extra_data:
            msg.update(extra_data)

        eid = self.db.insert(msg)

        Mailbox = Query()

        # Mailbox to link mail
        mailboxes = []
        if incoming:
            mailboxes.append((msg['from'].addr_spec, msg['from'].display_name)) # store only in `from` box
        else:
            if len(to_addrs) == 1:
                to = to_addrs[0]
                mailboxes.append((to.addr_spec, to.display_name))
            else: # TODO Create group mailboxes
                for to in to_addrs: # Put in all recipients boxes
                    mailboxes.append((to.addr_spec, to.display_name))

        for mailbox_address, mailbox_name in mailboxes:
            # Get mailbox if exists or create it
            mailbox = await self.get_or_create_mailbox(account, mailbox_address, mailbox_name)

            # Update last_message date
            if mailbox['last_message'] is None or mailbox['last_message'] < msg['date']:
                mailbox['last_message'] = msg['date']

            mailbox_message_data = {
                'id': eid,
                'uid': msg['uid'],
                'date': msg['date']
            }

            mailbox['messages'].append(mailbox_message_data)

            self.db.update(mailbox, (Mailbox.type == 'mailbox') & (Mailbox.uid == mailbox['uid']))

        return msg

    async def get_mailboxes(self, account):
        """ Return all mailboxes in db with unread message count and total """

        Mailbox = Query()
        Message = Query()

        mailboxes = list(self.db.search((Mailbox.type=='mailbox') & (Mailbox['account'] == account.name)))
        for mailbox in mailboxes:
            mailbox['total'] = len(mailbox['messages'])
            mailbox['unreads'] = 0
            for message in mailbox['messages']:
                msg = await self.get(Message.uid==message['uid'])
                mailbox['unreads']  += 1 if msg.get('unread') else 0

        # TODO Hacky
        for m in mailboxes:
            if not isinstance(m['last_message'], datetime.datetime):
                m['last_message'] = arrow.get(m['last_message']).datetime

        return mailboxes

    async def get_mailbox(self, account, mailbox_id):
        """ Return the selected mailboxx """
        Mailbox = Query()
        Message = Query()

        mailbox = await self.get((Mailbox.uid==mailbox_id) & (Mailbox['account'] == account.name))

        messages = []
        mailbox['total'] = len(mailbox['messages'])
        mailbox['unreads'] = 0
        for message in mailbox['messages']:
            msg = await self.get(Message.uid==message['uid'])
            msg = dict(msg)
            del msg['body']
            mailbox['unreads']  += 1 if msg.get('unread') else 0
            messages.append(msg)

        mailbox['messages'] = messages

        # TODO reverse me
        for m in messages:
            if not isinstance(m['date'], datetime.datetime):
                m['date'] = arrow.get(m['date']).datetime

        return mailbox

    async def get_mail(self, account, mail_uid):
        """ Get message by uid """

        Message = Query()

        mail = await self.get((Message.uid==mail_uid) & (Message['account'] == account.name))

        if not isinstance(mail['date'], datetime.datetime):
            mail['date'] = arrow.get(mail['date']).datetime

        return mail

    async def get_mail_attachment(self, account, mail_uid, att_index):
        """ Return a specific mail attachment """

        Message = Query()

        mail = await self.get((Message.uid==mail_uid) & (Message['account'] == account.name))
        raw_mail = await self.get_content_msg(mail_uid)

        attachment = mail['attachments'][att_index]

        atts = list(raw_mail.iter_attachments())
        stream = atts[att_index]

        content = stream.get_content()
        return attachment, content

    async def update_mail(self, account, mail):
        """ Update any mail """

        Message = Query()

        self.db.update(mail, (Message.uid==mail['uid']) & (Message['account'] == account.name))

        return mail

    async def save_user_session(self, session_key, session):
        """ Save modified user session """
        Session = Query()

        session_from_storage = await self.get_user_session(session_key)
        session_from_storage.update(session)

        self.db.update(session_from_storage, (Session.type == 'session') & (Session.key==session_key))

    async def get_user_session(self, session_key):
        """ Load user session """

        Session = Query()
        return await self.get_or_create(
            (Session.type=='session') & (Session.key==session_key),
            {'type': 'session', 'key': session_key}
        )

    async def contacts_search(self, account, text):
        """ Search a contact from mailboxes """

        Mailbox = Query()

        results = self.db.search(
            (Mailbox.type=='mailbox') & 
            (Mailbox['account'] == account.name) &
            (Mailbox['address'].search(text))
        )

        return [r['address'] for r in results[:10]]






