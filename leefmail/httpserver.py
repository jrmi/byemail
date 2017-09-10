import asyncio
import datetime

from sanic import Sanic
from sanic.response import json

from tinydb import Query

from leefmail.mailstore import storage

app = Sanic(__name__)

@app.route("/mailboxes")
async def mailboxes(request):
    mbxs = await storage.get_mailboxes()
    for m in mbxs:
        if isinstance(m['last_message'], datetime.datetime): # Also strange hack
          m['last_message'] = m['last_message'].isoformat()
    return json(mbxs)

@app.route("/mailbox/<mailbox_eid>")
async def mailbox(request, mailbox_eid):
    mailbox_to_return = await storage.get_mailbox(int(mailbox_eid))
    for m in mailbox_to_return['messages']:
        m['date'] = m['date'].isoformat()
    return json(mailbox_to_return)

@app.route("/mail/<mail_eid>")
async def mailb(request, mail_eid):
    mail_to_return = await storage.get_mail(int(mail_eid))
    mail_to_return['date'] = mail_to_return['date'].isoformat()
    return json(mail_to_return)
