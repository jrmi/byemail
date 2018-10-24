import re
import uuid
import arrow
import base64
import logging
import datetime

from functools import wraps
from json import JSONEncoder, JSONDecoder

from email import policy
from email.parser import BytesParser
from email.headerregistry import Address
from email.errors import InvalidHeaderDefect

from tortoise import Tortoise
from tortoise import fields
from tortoise import exceptions
from tortoise.models import Model

from byemail.storage import core, DoesntExists, MultipleResults

logger = logging.getLogger(__name__)

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
        try:
            return Address(display_name=s['display_name'], addr_spec=s['addr_spec'])
        except InvalidHeaderDefect:
            return ''

        

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


def translate_exception():
    def translate(func):
        @wraps(func)
        async def func_wrap(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions.DoesNotExist:
                raise DoesntExists()
            except exceptions.MultipleObjectsReturned:
                raise MultipleResults()
            
        return func_wrap

    return translate

# Mailbox
class Mailbox(Model):
    id = fields.IntField(pk=True)
    uid = fields.CharField(max_length=255)
    account = fields.CharField(max_length=255)
    address = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    unreads = fields.IntField(default=0)
    total = fields.IntField(default=0)
    last_message = fields.DatetimeField(null=True)

    def __str__(self):
        return f"<Mailbox {self.account}(<{self.name}> {self.address})>"

    def as_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'account': self.account,
            'address': self.address,
            'name': self.name,
            'total': self.total,
            'unreads': self.unreads,
            'last_message': self.last_message,
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

    def update_from_dict(self, data):
        data = dict(data)
        self.uid = data.pop('uid')
        self.status = data.pop('status')
        self.unread = data.pop('unread')
        self.timestamp = data.pop('date')
        self.incoming = data.pop('incoming')
        self.attachments = data.pop('attachments')
        self.data = data

    def as_dict(self):
        data = dict(self.data)
        data['uid'] = self.uid
        data['status'] = self.status
        data['unread'] = self.unread
        data['date'] = self.timestamp
        data['incoming'] = self.incoming
        data['attachments'] = self.attachments
        
        return data

    def as_mini_dict(self):
        data = self.as_dict()
        del data['body']

        return data


class RawMessage(Model):
    """ Raw message content is stored here """
    id = fields.IntField(pk=True)
    uid = fields.CharField(max_length=255)

    content = fields.TextField()

class RawMail(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(max_length=255)
    peer = fields.CharField(max_length=255),
    host_name =  fields.CharField(max_length=255),
    mail_from = fields.CharField(max_length=255),
    tos =  fields.CharField(max_length=255),
    subject = fields.CharField(max_length=255),
    received = fields.DatetimeField(),

    data = fields.TextField()

    @staticmethod
    def from_dict(data):
        rm = RawMail()
        rm.status = data['status']
        rm.peer = data['peer']
        rm.host_name = data['host_name']
        rm.mail_from = data['from']
        rm.tos = data['tos']
        rm.subject = data['subject']
        rm.received = datetime.datetime.now().isoformat()
        rm.data = data['data']

        return rm

class Session(Model):
    """ Users session """

    id = fields.IntField(pk=True)
    key = fields.CharField(max_length=255)

    content = fields.JSONField(default=list)

    def as_dict(self):
        return self.content


class Backend(core.Backend):

    def __init__(self, config=None, uri=None, **kwargs):
        super().__init__(**kwargs)
        assert config != None or uri != None, "You need to specify at least one of uri or config param"
        self.config = config
        self.uri = uri

    async def start(self):
        if self.config:
            config = {
                'connections': self.config,
                'apps': {
                    'models': {
                        'models': ['byemail.storage.sqldb'],
                        'default_connection': 'default',
                    }
                }
            }

            await Tortoise.init(config=config)

        if self.uri:
            await Tortoise.init(
                db_url=self.uri,
                modules={'models': ['byemail.storage.sqldb']}
            )

        try:
            await Tortoise.generate_schemas()
        except exceptions.OperationalError:
            logger.warning("No database initialisation, db seems existing...")

    async def stop(self):
        await Tortoise.close_connections()

    async def store_bad_msg(self, bad_msg):
        """ To handle msg that failed to parse """
        rm = RawMail.from_dict(bad_msg)
        await rm.save()

    async def store_content(self, uid, content):
        """ Store raw message content """
        b64_content = base64.b64encode(content).decode('utf-8')

        rmsg = RawMessage(uid=uid, content=b64_content)
        return await rmsg.save()

    @translate_exception()
    async def get_content_msg(self, uid):
        """ Return EmailMessage instance for this message uid """
        rmsg = await RawMessage.get(uid=uid)

        b64_content = rmsg.content

        msg = BytesParser(policy=policy.default).parsebytes(base64.b64decode(b64_content))

        return msg

    @translate_exception()
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

    @translate_exception()
    async def get_mailboxes(self, account):
        """ Return all mailboxes in db with unread message count and total """
        return [m.as_dict() for m in await Mailbox.filter(account=account.name)]

    @translate_exception()
    async def get_mailbox(self, account, mailbox_id):
        """ Return the selected mailbox """
        
        mailbox = await Mailbox.get(uid=mailbox_id, account=account.name)

        msgs = await Message.filter(mailboxes = mailbox.id).order_by('timestamp')

        result = mailbox.as_dict()
        result['messages'] = [msg.as_mini_dict() for msg in msgs]

        return result

    @translate_exception()
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

        # Add information
        msg['uid'] = uuid.uuid4().hex
        msg['incoming'] = incoming
        msg['unread'] = incoming
        msg['status'] = 'new'

        # Create dbmessage
        dbmsg = Message()
        dbmsg.update_from_dict(msg)
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

            # Update last_message date
            if mailbox.last_message is None or mailbox.last_message <  msg['date']:
                mailbox.last_message = msg['date']

            # Update unread count
            #print(await mailbox.messages.filter(unread=1).count()) # TODO fails
            #print(list(mailbox.messages.all())) # TODO fails
            mailbox.unreads = len(list(await mailbox.messages.filter(unread=1)))
            mailbox.total = len(list(await mailbox.messages.filter(uid__icontains='')))

            await mailbox.save()

        return dbmsg.as_dict()

    @translate_exception()
    async def get_mail(self, account, mail_uid):
        """ Get message by uid """
        mail = await Message.get(uid=mail_uid, mailboxes__account=account.name)
        return mail.as_dict()

    @translate_exception()
    async def update_mail(self, account, mail):
        """ Update any mail """
        dbmsg = await Message.get(uid=mail['uid'], mailboxes__account=account.name)
        dbmsg.update_from_dict(mail)

        await dbmsg.save()

        return dbmsg.as_dict()

    @translate_exception()
    async def get_mail_attachment(self, account, mail_uid, att_index):
        """ Return a specific mail attachment """

        mail = await self.get_mail(account, mail_uid)
        raw_mail = await self.get_content_msg(mail_uid)

        attachment = mail['attachments'][att_index]

        atts = list(raw_mail.iter_attachments())
        stream = atts[att_index]
        content = stream.get_content()

        return attachment, content

    @translate_exception()
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

    @translate_exception()
    async def get_user_session(self, session_key):
        """ Load user session """
        session, _ = await Session.get_or_create(
            defaults = {
                'content': {}
            },
            key=session_key
        )
        return session.as_dict()

    @translate_exception()
    async def contacts_search(self, account, text):
        """ Search a contact from mailboxes """
        matching_mailboxes = await Mailbox.filter(address__icontains=text, account=account.name)
        return [m.address for m in matching_mailboxes]






