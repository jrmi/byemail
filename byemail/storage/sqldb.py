import re
import uuid
import arrow
import base64
import datetime

from json import JSONEncoder, JSONDecoder

from email import policy
from email.parser import BytesParser
from email.headerregistry import Address
from email.errors import InvalidHeaderDefect

from tortoise import Tortoise
from tortoise import fields
from tortoise import exceptions
from tortoise.models import Model

from byemail.storage import core


class DateTimeSerializer():
    OBJ_CLASS = datetime.datetime  # The class this serializer handles

    def encode(self, obj):
        return {
            '_object_class': self.OBJ_CLASS.__name__,
            'date': arrow.get(obj).for_json()
        } 

    def decode(self, s):
        return arrow.get(s['date']).datetime

class AddressSerializer():
    OBJ_CLASS = Address  # The class this serializer handles

    def encode(self, obj):
        return {
            '_object_class': self.OBJ_CLASS.__name__,
            'addr_spec': obj.addr_spec,
            'display_name': obj.display_name
        }

    def decode(self, s):
        return Address(display_name=s['display_name'], addr_spec=s['addr_spec'])

encoders = [DateTimeSerializer(), AddressSerializer()]

class MyJSONEncoder(JSONEncoder):
   def default(self, obj):
        for encoder in encoders:
            if isinstance(obj, encoder.OBJ_CLASS):
                return encoder.encode(obj)
        else:
            return super().default(obj)

class MyJSONDecoder(JSONDecoder):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, object_hook=self.object_hook, **kwargs)
    
    def object_hook(self, obj):
        if '_object_class' in obj:
            for decoder in encoders:
                if decoder.OBJ_CLASS.__name__ == obj['_object_class']:
                    return decoder.decode(obj)
        return obj


# Mailbox
class Mailbox(Model):
    id = fields.IntField(pk=True)
    uid = fields.CharField(max_length=255)
    account = fields.CharField(max_length=255)
    address = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    unreads = fields.IntField(default=0)
    total = fields.IntField(default=0)

    def __str__(self):
        return f"<Mailbox {self.account}(<{self.name}> {self.address})>"

    def as_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'account': self.account,
            'address': self.address,
            'name': self.name,
            'totals': self.total,
            'unreads': self.unreads
        }


# Message
class Message(Model):
    id = fields.IntField(pk=True)
    uid = fields.CharField(max_length=255)

    mailboxes = fields.ManyToManyField('models.Mailbox', related_name='messages')

    status = fields.CharField(max_length=255)
    timestamp = fields.DatetimeField()
    unread = fields.BooleanField()
    incoming = fields.BooleanField()
    #body = fields.TextField()

    attachments = fields.JSONField(default=[])
    data = fields.JSONField(encoder=MyJSONEncoder().encode, decoder=MyJSONDecoder().decode)
    #raw_message = fields.TextField()

    def update_from_dict(self, data):
        self.uid = data['uid']
        self.status = data['status']
        self.unread = data['unread']
        self.timestamp = data['received']
        self.incoming = data['incoming']
        self.attachments = data['attachments']
        self.data = data

    def as_dict(self):
        data = self.data
        data['uid'] = self.uid
        data['status'] = self.status
        data['unread'] = self.unread
        data['incoming'] = self.incoming
        
        return data


class RawMessage(Model):
    """ Raw message content is stored here """
    id = fields.IntField(pk=True)
    uid = fields.CharField(max_length=255)

    content = fields.TextField()


class Session(Model):
    """ Users session """

    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=255)

    content = fields.JSONField(default=list)

    def as_dict(self):
        return self.content


class Backend(core.Backend):

    def __init__(self, uri="sqlite://:memory:", **kwargs):
        super().__init__(**kwargs)
        self.uri = uri

    async def start(self):
        await Tortoise.init(
            db_url=self.uri,
            modules={'models': ['byemail.storage.sqldb']}
        )

        await Tortoise.generate_schemas()

    async def stop(self):
        await Tortoise.close_connections()

    async def store_bad_msg(self, bad_msg):
        """ To handle msg that failed to parse """
        raise NotImplementedError()

    async def store_content(self, uid, content):
        """ Store raw message content """
        b64_content = base64.b64encode(content).decode('utf-8')

        rmsg = RawMessage(uid=uid, content=b64_content)
        return await rmsg.save()

    async def get_content_msg(self, uid):
        """ Return EmailMessage instance for this message uid """
        rmsg = await RawMessage.get(uid=uid)

        b64_content = rmsg.content

        msg = BytesParser(policy=policy.default).parsebytes(base64.b64decode(b64_content))

        return msg

    async def get_or_create_mailbox(self, account, address, name):
        """ Create a mailbox """

        mailbox, _ = await Mailbox.get_or_create(
            defaults=dict(
                uid=uuid.uuid4().hex
            ),
            account=account.name, 
            address=address, 
            name=name
        )

        return mailbox

    async def get_mailboxes(self, account):
        """ Return all mailboxes in db with unread message count and total """
        return [m.as_dict() for m in await Mailbox.filter(account=account.name)]

    async def get_mailbox(self, mailbox_id):
        """ Return the selected mailbox """
        
        mailbox = await Mailbox.get(uid=mailbox_id)

        msgs = await Message.filter(mailboxes = mailbox.id).order_by('timestamp')

        result = mailbox.as_dict()
        result['messages'] = [msg.as_dict() for msg in msgs]

        return result

    async def store_msg(
        self, 
        msg, 
        account, 
        from_addr, 
        to_addrs, 
        incoming=True, 
        extra_data=None
    ):
        """ Store message in database """

        dbmsg = Message(uid=uuid.uuid4().hex)
        dbmsg.incoming = incoming
        dbmsg.unread = incoming
        dbmsg.status = 'new'
        dbmsg.timestamp = msg['received']
        dbmsg.data = msg

        await dbmsg.save()

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

            await dbmsg.mailboxes.add(mailbox)

            if extra_data:
                msg.data.update(extra_data)

        
        # Update unread count
        mailbox.unreads = len(list(await mailbox.messages.filter(unread='true')))
        mailbox.totals = len(list(await mailbox.messages.filter(id__gte=0)))
        await mailbox.save()

        return dbmsg.as_dict()

    async def get_mail(self, mail_uid):
        """ Get message by uid """
        mail = await Message.get(uid=mail_uid)
        return mail.as_dict()

    async def update_mail(self, mail):
        """ Update any mail """
        dbmsg = await Message.get(uid=mail['uid'])
        dbmsg.update_from_dict(mail)

        await dbmsg.save()

        return dbmsg.as_dict()

    async def get_mail_attachment(self, mail_uid, att_index):
        """ Return a specific mail attachment """

        mail = await self.get_mail(mail_uid)
        raw_mail = await self.get_content_msg(mail_uid)

        attachment = mail['attachments'][att_index]

        atts = list(raw_mail.iter_attachments())
        stream = atts[att_index]

        content = stream.get_content()
        return attachment, content

    async def save_user_session(self, session_key, session):
        """ Save modified user session """
        dbsession, _ = await Session.get_or_create(
            defaults = {
                'content': {}
            },
            key=session_key
        )

        dbsession.content = session
        await dbsession.save()

    async def get_user_session(self, session_key):
        """ Load user session """
        session, _ = await Session.get_or_create(
            defaults = {
                'content': {}
            },
            key=session_key
        )
        return session.as_dict()

    async def contacts_search(self, account, text):
        """ Search a contact from mailboxes """
        raise NotImplementedError()






