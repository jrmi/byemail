import time
import base64
import datetime

from email import policy
from email.utils import localtime
from email.message import EmailMessage
from email.headerregistry import AddressHeader, HeaderRegistry

import magic
import dkim

from byemail.conf import settings

def parse_email(email_str):
    """ Helper to pars an email address from client """
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
    msg['Message-Id'] =  "<{}-{}>".format(time.time(), from_addr)

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

    # TODO Open key one for all
    with open(settings.DKIM_CONFIG['private_key']) as key:
        private_key = key.read()

    # Generate message signature
    sig = dkim.sign(
        msg.as_bytes(), 
        settings.DKIM_CONFIG['selector'].encode(), 
        settings.DKIM_CONFIG['domain'].encode(), 
        private_key.encode(), 
        identity=from_addr,
        include_headers=[s.encode() for s in settings.DKIM_CONFIG['headers']]
    )
    # Clean de generated signature
    sig = sig.decode().replace('\r\n ', '').replace('\r\n', '')

    # Add the DKIM-Signature
    msg['DKIM-Signature'] = sig[len("DKIM-Signature: "):]

    return msg

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
