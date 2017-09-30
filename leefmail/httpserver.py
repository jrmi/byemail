import os
import asyncio
import datetime
import logging

from sanic import Sanic
from sanic.response import json, redirect

from tinydb import Query

from leefmail.mailstore import storage

from leefmail.smtpserver import MailSender

logger = logging.getLogger(__name__)

app = Sanic(__name__)

BASE_DIR = os.path.dirname(__file__)

app.static('/static', os.path.join(BASE_DIR, '../client/dist/static'))
app.static('/index.html', os.path.join(BASE_DIR, '../client/dist/index.html'))

@app.route('/')
async def index(request):
    return redirect('/index.html')

@app.route("/api/mailboxes")
async def mailboxes(request):
    mbxs = await storage.get_mailboxes()
    for m in mbxs:
        if isinstance(m['last_message'], datetime.datetime): # Also strange hack
            m['last_message'] = m['last_message'].isoformat()
    return json(mbxs)

@app.route("/api/mailbox/<mailbox_id>")
async def mailbox(request, mailbox_id):
    mailbox_to_return = await storage.get_mailbox(mailbox_id)
    for m in mailbox_to_return['messages']:
        if isinstance(m['date'], datetime.datetime): # Also strange hack
            m['date'] = m['date'].isoformat()
    return json(mailbox_to_return)

@app.route("/api/mail/<mail_id>")
async def mailb(request, mail_id):
    mail_to_return = await storage.get_mail(mail_id)
    if isinstance(mail_to_return['date'], datetime.datetime): # Also strange hack
        mail_to_return['date'] = mail_to_return['date'].isoformat()
    return json(mail_to_return)


@app.route("/api/sendmail/", methods=['POST'])
async def sendmail(request):
    data = request.json
    print(data)

    # Message construction
    from email.message import EmailMessage
    from email import policy
    from email.headerregistry import Address
    from email.utils import localtime

    from email.policy import EmailPolicy
    from email.headerregistry import HeaderRegistry
    from email.headerregistry import AddressHeader

    content = data['content']
    subject = data['subject']

    to_addrs = []
    for to in data['to_addrs']:
        to_addrs.append(Address(display_name=to['display_name'], addr_spec=to['addr_spec']))

    from_addr = Address(display_name=data['from']['display_name'], addr_spec=data['from']['addr_spec'])

    #subject = "Un sujet pour les rois"


    # TODO remove when tested

    '''to_addrs = [
        Address(display_name="Jrmi sur jeremiez", addr_spec="jrmi@jeremiez.net"),
        Address(display_name="Jeremie sur jeremiez", addr_spec="jeremie@jeremiez.net"),
        Address(display_name="Jeremie sur jeremiez", addr_spec="titi@mailtest.jeremiez.net"),
        Address(display_name="Jeremie sur free", addr_spec="jrmi@free.fr"),
        #Address(display_name="Toto", addr_spec="toto@localhost")
    ]'''

    #from_addr = Address(display_name="Test", addr_spec="test@mailtest.jeremiez.net")

    # To have a correct address header
    header_registry = HeaderRegistry()
    header_registry.map_to_type('To', AddressHeader)
    mypolicy = EmailPolicy(header_factory=header_registry)
    msg = EmailMessage(mypolicy)

    msg.set_content(content)
    msg['From'] = from_addr
    msg['Subject'] = subject
    msg['To'] = to_addrs
    msg['Date'] = localtime()

    mail_sender = MailSender()

    result = await mail_sender.send(
        msg,
        from_addr=from_addr.addr_spec,
        to_addrs=[a.addr_spec for a in to_addrs]
    )

    response = {'Ok'}
    return json(response)




