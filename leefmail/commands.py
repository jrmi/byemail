#!/usr/bin/env python

# ############################################################################
# This is the code for THE leefmail command line program
# and all it's related commands
# ############################################################################

import os
import sys
import asyncio

import uvloop
import begin

import leefmail
from leefmail.conf import settings
from leefmail import smtpserver, httpserver
from aiosmtpd.controller import Controller

# For slimta
from slimta.relay.smtp.mx import MxSmtpRelay
import shelve
from slimta.queue.dict import DictStorage
from slimta.queue import Queue
from slimta.policy.headers import *
from slimta.policy.split import RecipientDomainSplit
from slimta.edge.smtp import SmtpEdge

# TODO: remove below if statement asap. This is a workaround for a bug in begins
# TODO: which provokes an eception when calling pypeman without parameters.
# TODO: more info at https://github.com/aliles/begins/issues/48
if len(sys.argv) == 1:
    sys.argv.append('-h')

# Keep this import
sys.path.insert(0, os.getcwd())

@begin.subcommand
def start(reload: 'Make server autoreload (Dev only)'=False,):
    """ Start leefmail """

    settings.init_settings()

    controller = Controller(smtpserver.MSGHandler(), **settings.SMTP_CONF)
    controller.start()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    server = httpserver.app.create_server(**settings.HTTP_CONF)
    task = asyncio.ensure_future(server)

    try:
        print("Server started on %s:%d" % (controller.hostname, controller.port))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping")

    controller.stop()


'''@begin.subcommand
def smtp():

    #from slimta.smtp.auth import Auth, CredentialsInvalidError

    tls_args = {'keyfile': '/path/to/key.pem', 'certfile': '/path/to/cert.pem'}
    relay = MxSmtpRelay(connect_timeout=20, command_timeout=10, tls_immediately=False,
                                    data_timeout=20, idle_timeout=30, tls_required=False)


    env_db = shelve.open('envelope.db')
    meta_db = shelve.open('meta.db')
    storage = DictStorage(env_db, meta_db)
    queue = Queue(storage, relay)
    queue.start()

    queue.add_policy(AddDateHeader())
    queue.add_policy(AddMessageIdHeader())
    queue.add_policy(AddReceivedHeader())

    queue.add_policy(RecipientDomainSplit())

    # Your edge creation line would now look like...
    edge = SmtpEdge(('', 3587), queue, auth=False)
    edge.start()

    try:
        edge.get()
    except KeyboardInterrupt:
        pass'''

@begin.start
def run(version=False):
    """ Leefmail """
    if version:
        print(leefmail.__version__)
        sys.exit(0)



