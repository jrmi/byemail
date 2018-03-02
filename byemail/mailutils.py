import datetime
import base64
import magic

from email import policy
from email.utils import localtime
from email.message import EmailMessage
from email.headerregistry import AddressHeader, HeaderRegistry


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
