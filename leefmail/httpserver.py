import asyncio

from sanic import Sanic
from sanic.response import json

from tinydb import Query

from leefmail import store
from leefmail.mailstore import storage

app = Sanic(__name__)

@app.route("/mailboxes")
async def test(request):
    return json(await storage.get_mailboxes())

