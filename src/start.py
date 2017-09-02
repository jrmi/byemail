#!/bin/env python

import os
import asyncio
import base64
import datetime
import mimetypes

from aiosmtpd.handlers import Message
from aiosmtpd.controller import Controller

from tinydb import TinyDB, Query


class DBHandler2:

    def __init__(self):
        super().__init__()
        self.db = TinyDB('db.json')


    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not address.endswith('@localhost'):
            return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        #print(envelope.content.decode('utf8', errors='replace'))
        print('End of message')

        self.db.insert({
            'type': 'mail', 
            'peer': session.peer,
            'host_name': session.host_name,
            'from': envelope.mail_from,
            'for': envelope.rcpt_tos,
            'received': datetime.datetime.now().isoformat(),
            'data': base64.b64encode(envelope.content).decode('utf-8')
        })

        return '250 Message accepted for delivery'

class DBHandler(Message):

    def __init__(self):
        super().__init__()
        self.db = TinyDB('db.json')

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not address.endswith('@localhost'):
            return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    def handle_message(self, msg):
        print(msg)
        print(msg['From'])
        print(msg.as_string())

        counter = 1
        for part in msg.walk():
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                continue
            # Applications should really sanitize the given filename so that an
            # email message can't be used to overwrite important files
            filename = part.get_filename()
            if not filename:
                ext = mimetypes.guess_extension(part.get_content_type())
                if not ext:
                    # Use a generic bag-of-bits extension
                    ext = '.bin'
                filename = 'part-%03d%s' % (counter, ext)
            counter += 1
            print("PJ %s " % filename)

            #with open(os.path.join(args.directory, filename), 'wb') as fp:
            #    fp.write(part.get_payload(decode=True))


        '''self.db.insert({
            'type': 'mail', 
            'from': msg.get(FROM),
            'for': envelope.rcpt_tos,
            'data': str(base64.b64encode(envelope.content))
        })'''

if __name__ == "__main__":
    controller = Controller(DBHandler2())

    controller.start()


    loop = asyncio.get_event_loop()
    try:
        print("Server started on %s:%d" % (controller.hostname, controller.port))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping")

    controller.stop()