import os
import asyncio
import datetime
import logging

from sanic import Sanic
from sanic.response import json, redirect

from tinydb import Query

from leefmail.mailstore import storage

from leefmail.mta import MailSender

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

    mail_sender = MailSender()

    msg = await mail_sender.make_msg_from_data(data)

    from_addr = data['from']['addr_spec']
    to_addrs = [a['addr_spec'] for a in data['to_addrs']]

    # First we store it
    await storage.store_msg(
        msg,
        from_addr=from_addr,
        to_addrs=to_addrs,
        mailbox_id=data['mailbox_id'],
        extra_data={'reply': True},
        extra_mailbox_data={'reply': True}
    )

    result = await mail_sender.send(
        msg,
        from_addr=from_addr,
        to_addrs=to_addrs
    )

    response = {'Ok'}
    return json(response)




