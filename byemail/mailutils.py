import re
import time
import base64
import datetime
import logging
import importlib
from collections import OrderedDict

from email import policy
from email.utils import localtime, make_msgid
from email.message import EmailMessage
from email.headerregistry import AddressHeader, HeaderRegistry

import magic

from byemail.conf import settings

logger = logging.getLogger(__name__)

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
    msg['Message-ID'] =  make_msgid()

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

    # TODO add html alternative
    # See https://docs.python.org/3.6/library/email.examples.html

    """msg.add_alternative("\
    <html>
    <head></head>
    <body>
        <p>{body}<p>
    </body>
    </html>
    "".format(content, subtype='html')"""

    return msg

async def extract_data_from_msg(msg):
    """ Extract data from a message to save it """
    logger.debug(msg)

    body = msg.get_body(('html', 'plain',))

    # Fix missing date
    if msg['Date'] is None:
        msg['Date'] = datetime.datetime.now()

    msg_out = {
        'status': 'new',
        'subject': msg['Subject'],
        # TODO rename this field
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
        'body-type': body.get_content_type() if body else "text/plain",
        'body-charset': body.get_content_charset() if body else "utf-8",
        'body': body.get_content() if body else "Body not found",
        'attachments': []
    }

    if msg['Cc']:
        msg_out['carboncopy'] = list(msg['Cc'].addresses)

    for ind, att in enumerate(msg.iter_attachments()):
        msg_out['attachments'].append({
            'index': ind,
            'type': att.get_content_type(),
            'filename': att.get_filename(),
            'content-id': att['content-id'][1:-1] if att['content-id'] else None
        })

    if msg['Thread-Topic']:
        msg_out['in-thread'] = True
        msg_out['thread-topic'] = msg['Thread-Topic']
        msg_out['thread-index'] = msg['Thread-index']

    return msg_out

async def apply_middlewares(msg, from_addr, recipients, incoming=True):
    """ Apply all configured incoming and outgoing middlewares """

    if incoming:
        middlewares = settings.INCOMING_MIDDLEWARES 
    else:
        middlewares = settings.OUTGOING_MIDDLEWARES

    for middleware in middlewares:
        try:
            module, _, func = middleware.rpartition(".")
            mod = importlib.import_module(module)
        except ModuleNotFoundError:
            logger.error("Module %s can't be loaded !", middleware)
            raise
        else:
            await getattr(mod, func)(
                msg, 
                from_addr=from_addr, 
                recipients=recipients, 
                incoming=incoming
            )


RE_CID = re.compile(r'cid:([^">]+)[">]?')

async def convert_cid_link(msg):
    """ Convert content-id tag to url """
    
    if msg['body-type'] == 'text/html':
        cids = {att['content-id']: att for att in msg['attachments']}

        body = msg['body']

        result = RE_CID.findall(body)
        for cid in result:
            if cid in cids:
                url = cids[cid]['url']
                body = body.replace(f'cid:{cid}', f'{settings.DOMAIN}{url}')

        msg['body'] = body

    return msg


