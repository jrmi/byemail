#!/usr/bin/env python

# ############################################################################
# This is the code for THE leefmail command line program
# and all it's related commands
# ############################################################################

import os
import sys
import asyncio

import begin

import leefmail
from leefmail import smtpserver, httpserver
from aiosmtpd.controller import Controller

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

    controller = Controller(smtpserver.MSGHandler())
    controller.start()

    loop = asyncio.get_event_loop()

    server = httpserver.app.create_server(host="0.0.0.0", port=8000)
    task = asyncio.ensure_future(server)

    try:
        print("Server started on %s:%d" % (controller.hostname, controller.port))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping")

    controller.stop()

@begin.start
def run(version=False):
    """ Leefmail """
    if version:
        print(leefmail.__version__)
        sys.exit(0)