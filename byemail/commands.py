#!/usr/bin/env python

# ############################################################################
# This is the code for THE byemail command line program
# and all it's related commands
# ############################################################################

import os
import sys
import asyncio

import uvloop
import begin

import byemail
from byemail.conf import settings
from byemail import smtpserver, httpserver
from aiosmtpd.controller import Controller


# TODO: remove below if statement asap. This is a workaround for a bug in begins
# TODO: which provokes an exception when calling command without parameters.
# TODO: more info at https://github.com/aliles/begins/issues/48
if len(sys.argv) == 1:
    sys.argv.append('-h')

# Keep this import
sys.path.insert(0, os.getcwd())

@begin.subcommand
def start(reload: 'Make server autoreload (Dev only)'=False,):
    """ Start byemail """

    settings.init_settings()

    controller = Controller(smtpserver.MSGHandler(), **settings.SMTP_CONF)
    controller.start()

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    server = httpserver.app.create_server(**settings.HTTP_CONF)
    asyncio.ensure_future(server)

    try:
        print("Server started on %s:%d" % (controller.hostname, controller.port))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping")

    controller.stop()

@begin.start
def run(version=False):
    """ byemail """
    if version:
        print(byemail.__version__)
        sys.exit(0)



