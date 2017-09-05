import asyncio

from sanic import Sanic
from sanic.response import json

from tinydb import Query

from leefmail import store

app = Sanic(__name__)

class MailBackend():
    def __init__(self):
        super().__init__()

        loop = asyncio.get_event_loop()

        self.db = loop.run_until_complete(store.get_db())

    async def get_mailboxes(self):
        Mailbox = Query()

        mailboxes = list(self.db.search(Mailbox.type=='mailbox'))

        sorted_mailboxes = sorted(mailboxes, key=lambda x: x['last_message'], reverse=True)
        
        for mailbox in sorted_mailboxes:
            sorted_messages = sorted(mailbox['messages'], key=lambda x : x['date'], reverse=True)
            mailbox['messages'] = []
            for msg in sorted_messages:
                mailbox['messages'].append(self.db.get(eid=msg['id']))

        return sorted_mailboxes


mails = MailBackend()

@app.route("/mailboxes")
async def test(request):
    global mails
    return json(await mails.get_mailboxes())

