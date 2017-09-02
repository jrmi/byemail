#!/bin/env python

from tinydb import TinyDB, Query
import email
from datetime import datetime

import base64


def decode_header(text):
    """Decode a header value and return the value as a unicode string."""
    if not text:
        return text
    res = []
    for part, charset in email.header.decode_header(text):
        if isinstance(part, str):
            res.append(part)
        else:
            try:
                res.append(part.decode(charset or 'latin1', 'replace'))
            except LookupError:
                res.append(part.decode('utf-8', 'replace'))
    return ' '.join(res)

def parse_rfc2822_date(text):
    """Parse an rfc2822 date string into a datetime object."""
    t = email.utils.mktime_tz(email.utils.parsedate_tz(text))
    return datetime.utcfromtimestamp(t)


def handle_part(part):
    charset = part.get_content_charset('latin1')
    print(charset)
    ctype = part.get_content_type()
    mainctype = part.get_content_maintype()

    if ctype == 'text/plain':
        print('Text alternative')
        print(part.get_content())
        return

    if ctype == 'text/html':
        print('Html alternative')
        #print(part.get_payload(decode=True).decode(charset, 'replace'))
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
    db = TinyDB('db.json')

    for mail in db.all()[11:13]:
        #print(base64.b64decode(mail['data']).decode('utf-8'))
        msg = email.message_from_string(base64.b64decode(mail['data']).decode('utf-8'))

        print('----------')
        #print(mail['received'])
        print(decode_header(msg['Subject']))
        #print(decode_header(msg['From']))
        #print(msg['Return-Path'])
        #print(msg['To'])
        #print(msg['X-Original-To'])
        #print(parse_rfc2822_date(msg['Date']))
        #print(decode_header(msg['Thread-Topic']) or '')
        #print(msg['Thread-Index'] or '')

        try:
            if msg.is_multipart():
                for part in msg.walk():
                    handle_part(part)
                    
            else:
                handle_part(msg)
        except :
            print(msg)
            raise

        print('---\n\n\n')

            

    

