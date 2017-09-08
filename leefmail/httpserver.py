import asyncio

from sanic import Sanic
from sanic.response import json

from tinydb import Query

from leefmail.mailstore import storage

app = Sanic(__name__)

@app.route("/mailboxes")
async def mailboxes(request):
    return json(await storage.get_mailboxes())

@app.route("/mailbox/<mailbox_eid>")
async def mailbox(request, mailbox_eid):
    print(mailbox_eid)
    return json(await storage.get_mailbox(int(mailbox_eid)))