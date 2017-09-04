#!/bin/env python

import base64
import datetime

import email
from email import policy
from email.parser import BytesParser

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer, SerializationMiddleware

import arrow

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime.datetime  # The class this serializer handles

    def encode(self, obj):
        return arrow.get(obj).for_json()

    def decode(self, s):
        return arrow.get(s).datetime

class AddressSerializer(Serializer):
    OBJ_CLASS = email.headerregistry.Address  # The class this serializer handles

    def encode(self, obj):
        return "__|__".join([obj.addr_spec, obj.display_name])

    def decode(self, s):
        addr_spec, display_name = s.split('__|__')

        return email.headerregistry.Address(display_name=display_name, addr_spec=addr_spec)


def handle_part(part):
    charset = part.get_content_charset('latin1')
    ctype = part.get_content_type()
    mainctype = part.get_content_maintype()

    print(ctype, charset, part.get_content_disposition())

    if ctype == 'text/plain':
        print('Text alternative')
        #print(part.get_content())
        return

    if ctype == 'text/html':
        print('Html alternative')
        #print(part.get_content())
        return
    
    if mainctype == 'image':
        print('Image attachment')
        return

    if ctype == 'message/rfc822':
        print('A message attachment')
        return

    if ctype == 'text/x-vcard':
        print('A vcard attachment')
        return

    if mainctype == 'multipart':
        return

    print('Not handled type "%s"' % ctype)

if __name__ == "__main__":
        
    serialization = SerializationMiddleware()
    serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
    serialization.register_serializer(AddressSerializer(), 'TinyAddress')

    db = TinyDB('db.json', storage=serialization)

    Message = Query()
    Mailbox = Query()


    for mail in db.search(Message.type=='mail' and Message.status=='delivered')[:1]:
        msg = BytesParser(policy=policy.default).parsebytes(base64.b64decode(mail['data']))

        print('----------')
        print(mail['received'])
        print("Subject:", mail['subject'])
        print("From:", mail['from'])
        print("Return:", mail['return'])
        print("To:", mail['tos'])
        print("Orig-To:", mail['original-to'])
        print("Date:", mail['date'])
        if mail['in-thread']:
            print("Thread-Topic:", (mail['thread-topic']))
            print("Thread-Index:", (mail['thread-index']))

        print("Body type:", mail['main-body-type'])
        print("Attachements count:", len(mail['attachments']))

        for att in mail['attachments']:
            print("    - Att:", att['type'], att['filename'])

        print('---\n\n\n')


    for mail in db.search(Message.type=='mail' and Message.status=='error')[:1]:
        msg = BytesParser(policy=policy.default).parsebytes(base64.b64decode(mail['data']))

        print("Subject:", msg['Subject'])

        '''try:
            print("From:", msg['From'])
            print("Tos:", msg.get('To'))
        except email.errors.HeaderParseError:
            print('Missing header as error')'''
            
        print("-BODY")
        #body = msg.get_body()

        #handle_part(body)

        print("-ATTACHMENTS")
        for att in msg.iter_attachments():
            handle_part(att)

    print("---- Mailbox ----")
    mailboxes = list(db.search(Mailbox.type=='mailbox'))

    sorted_mailboxes = sorted(mailboxes, key=lambda x: x['last_message'], reverse=True)
    
    for mailbox in sorted_mailboxes:
        print('Mailbox for %s - last message: %s (#%d messages)' % (mailbox['from'], mailbox['last_message'], len(mailbox['messages'])))
        sorted_messages = sorted(mailbox['messages'], key=lambda x : x['date'], reverse=True)
        for msg in sorted_messages:
            message = db.search( (Mailbox.type == 'mail') & (Mailbox.status == 'delivered') & (Mailbox['id'] == msg['id']) )[0]
            print('    ', message['date'], message['subject'] )
        print('-')

