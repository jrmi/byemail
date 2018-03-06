import time
import base64
import datetime
from collections import OrderedDict

from email import policy
from email.utils import localtime, make_msgid
from email.message import EmailMessage
from email.headerregistry import AddressHeader, HeaderRegistry

import magic
import dkim

from byemail.conf import settings

def parse_email(email_str):
    """ Helper to parse an email address from client """
    # TODO make a more reliable function
    res = {}
    AddressHeader.parse(email_str, res)

    return res['groups'][0].addresses[0]

def make_msg(subject, content, from_addr, tos=None, ccs=None, attachments=None):

    from_addr = parse_email(from_addr)

    # To have a correct address header
    header_registry = HeaderRegistry()
    header_registry.map_to_type('To', AddressHeader)
    msg = EmailMessage(policy.EmailPolicy(header_factory=header_registry))

    msg.set_content(content)
    msg['From'] = from_addr
    msg['Subject'] = subject
    msg['Message-Id'] =  make_msgid()

    if tos:
        msg['To'] = tos
    if ccs:
        msg['Cc'] = ccs

    if attachments:
        for att in attachments:
            filename = att['filename']
            content = base64.b64decode(att['b64'])
            # Guess type here
            maintype, subtype = magic.from_buffer(content, mime=True).split('/')
            msg.add_attachment(
                content, 
                maintype=maintype, 
                subtype=subtype, 
                filename=filename
            )

    msg['Date'] = localtime()

    return msg

def gen_dkim_sign(msg):

    # TODO Open key one for all
    with open(settings.DKIM_CONFIG['private_key']) as key:
        private_key = key.read()

    identity = msg['From'].addresses[0].addr_spec.encode()

    # Generate message signature
    sig = dkim.sign(
        msg.as_bytes(), 
        settings.DKIM_CONFIG['selector'].encode(), 
        settings.DKIM_CONFIG['domain'].encode(), 
        private_key.encode(), 
        identity=identity,
        include_headers=[s.encode() for s in settings.DKIM_CONFIG['headers']],
        canonicalize=(b'relaxed',b'simple')
    )

    # Clean de generated signature
    sig = sig.decode().replace('\r\n ', '').replace('\r\n', '')

    # Add the DKIM-Signature
    signature = sig[len("DKIM-Signature: "):]

    return signature


def gen_dkim_sign2(msg):
    import hashlib
    import base64
    import rsa

    res = OrderedDict([
        ('v', "1"),
        ('a', "rsa-sha256"),
        ('c', "simple/simple"),
        ('d', ""),
        ('i', ""),
        ('q', "dns/txt"),
        ('s', ""),
        ('h', []),
        ('bh', ""),
        ('b', ""),
    ])

    # TODO Open key one for all
    with open(settings.DKIM_CONFIG['private_key']) as key:
        private_key = key.read()
        '''.replace('\n', '')\
            .replace('-----BEGIN RSA PRIVATE KEY-----', '')\
            .replace('-----END RSA PRIVATE KEY-----', '')'''

    res['i'] = msg['From'].addresses[0].addr_spec
    res['d'] = settings.DKIM_CONFIG['domain']
    res['s'] = settings.DKIM_CONFIG['selector']
    res['h'] = " : ".join(settings.DKIM_CONFIG['headers'])

    body = msg.get_body(('html', 'plain',))
    #print(body.get_content())
    body_content = body.get_content()

    #body_content = """\n"""
    if body_content.endswith('\n'):
        body_content = body_content[:-1]

    body_content = body_content.replace('\n', '\r\n')
    #print(len(body_content))
    #print(repr(body_content))
    computed = base64.b64encode(hashlib.sha256(body_content.encode()).digest())
    #print(computed)
    res['bh'] = computed.decode()

    #assert computed == b"2jUSOH9NhtVGCQWNr9BrIAPreKQjO6Sn7XIkfJVOzv8="

    to_be_signed = ""
    for header in settings.DKIM_CONFIG['headers']:
        to_be_signed += "{}: {}\r\n".format(header, msg[header])

    to_be_signed += "DKIM-Signature: {}\r\n".format("; ".join([ "%s=%s" % v for v in res.items()]))
    print(repr(msg.as_bytes()))
    print(to_be_signed)

    #key = RSA.importKey(private_key)
    #print(key.size())
    #print(key.sign(to_be_signed.encode(), 10))

    print(rsa.sign(to_be_signed.encode(), private_key, 'SHA-1'))


    return "; ".join([ "%s=%s" % v for v in res.items()])


async def extract_data_from_msg(msg):
    """ Extract data from a message to save it """

    body = msg.get_body(('html', 'plain',))

    msg_out = {
        'status': 'delivered',
        'subject': msg['Subject'],
        'received': datetime.datetime.now().isoformat(),
        'from': msg['From'].addresses[0],
        'recipients': list(msg['To'].addresses),
        'original-to': msg['X-Original-To'],
        'delivered-to': msg['Delivered-To'],
        'dkim-signature': msg['DKIM-Signature'],
        'message-id': msg['Message-ID'],
        'domain-signature': msg['DomainKey-Signature'],
        'date': msg['Date'].datetime,
        'return': msg['Return-Path'] or msg['Reply-To'],
        'in-thread': False,
        'body-type': body.get_content_type(),
        'body-charset': body.get_content_charset(),
        'body': body.get_content(),
        'attachments': []
    }

    for ind, att in enumerate(msg.iter_attachments()):
        msg_out['attachments'].append({
            'index': ind,
            'type': att.get_content_type(),
            'filename': att.get_filename()
        })

    if msg['Thread-Topic']:
        msg_out['in_thread'] = True
        msg_out['thread-topic'] = msg['Thread-Topic']
        msg_out['thread-index'] = msg['Thread-index']

    return msg_out
