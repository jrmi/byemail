#!/usr/bin/env python

# ############################################################################
# This is the code for THE byemail command line program
# and all it's related commands
# ############################################################################

import os
import sys
import shutil
import asyncio
import subprocess
from os import path
from urllib import request

import uvloop
import begin
from aiosmtpd.controller import Controller

import byemail
from byemail.conf import settings
from byemail import mailutils
from byemail import storage
from byemail.helpers import reloader

# TODO: remove below if statement asap. This is a workaround for a bug in begins
# TODO: which provokes an exception when calling command without parameters.
# TODO: more info at https://github.com/aliles/begins/issues/48
if len(sys.argv) == 1:
    sys.argv.append('-h')

# Keep this import
sys.path.insert(0, os.getcwd())

def main(loop):
    """ Main function """

    settings.init_settings()

    from byemail import smtp, httpserver
    from byemail.storage import storage

    controller = Controller(smtp.MsgHandler(), **settings.SMTP_CONF)
    controller.start()

    loop.run_until_complete(storage.start())

    app = httpserver.get_app()
    server = app.create_server(**settings.HTTP_CONF)
    asyncio.ensure_future(server, loop=loop)

    try:
        print("Server started on %s:%d" % (controller.hostname, controller.port))
        loop.run_forever()
    except KeyboardInterrupt:
        print("Stopping")

    loop.run_until_complete(storage.stop())
    controller.stop()

@begin.subcommand
def start(reload: 'Make server autoreload (Dev only)'=False,):
    """ Start byemail SMTP and HTTP servers """

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    reloader.reloader_opt(main, reload, 2, loop)

@begin.subcommand
def generatekeys():
    """ Generate DKIM specific keys """
    # TODO check exist to avoid accidental rewrite
    private_command = ['openssl', 'genrsa', '-out', settings.DKIM_CONFIG['private_key'], '1024']
    public_command = ['openssl', 'rsa', '-in', settings.DKIM_CONFIG['private_key'],
        '-out', settings.DKIM_CONFIG['public_key'], '-pubout']

    print("Generating private key {}".format(settings.DKIM_CONFIG['private_key']))
    process = subprocess.run(private_command)
    if process.returncode != 0:
        print("Error while generating private key. Process abort.")
        sys.exit(-1)

    print("Generating public key {}".format(settings.DKIM_CONFIG['private_key']))
    process = subprocess.run(public_command)
    if process.returncode != 0:
        print("Error while generating public key. Process abort.")
        sys.exit(-1)

MX_TPL = """{address_domain}. MX 10 {externalip}"""
SPF_TPL = """{address_domain}. TXT \"v=spf1 a mx ip4:{externalip} -all\""""
DKIM_TPL = """{dkim_selector}._domainkey.{dkim_domain}. TXT \"v=DKIM1; k=rsa; s=email; p={publickey}\""""
DMARC_TPL = """_dmarc.{address_domain}. TXT \"v=DMARC1; p=none\""""

@begin.subcommand
def dnsconfig():
    """ Show configuration to apply to your DNS """
    context = {}

    print("# This is the guessed configuration for your domain.")
    print("# Remember you should execute this command on the server where")
    print("# you start byemail.")

    for account in settings.ACCOUNTS:
        result = []
        context['externalip'] = request.urlopen('https://api.ipify.org/').read().decode('utf8')
        context['address_domain'] = mailutils.parse_email(account['address']).domain
        context['dkim_selector'] = settings.DKIM_CONFIG['selector']
        context['dkim_domain'] = settings.DKIM_CONFIG['domain']

        '''with open(settings.DKIM_CONFIG['public_key']) as key:
            context['publickey'] = key.read().replace('\n', '')\
                .replace('-----BEGIN PUBLIC KEY-----', '')\
                .replace('-----END PUBLIC KEY-----', '')'''

        result.append(MX_TPL.format(**context))
        result.append(SPF_TPL.format(**context))
        #result.append(DKIM_TPL.format(**context))
        result.append(DMARC_TPL.format(**context))

        print(f"\n# For account {account['name']}, domain {context['address_domain']}\n")
        print('\n'.join(result))
        
    print()


@begin.subcommand
def init():
    """ Initialize a new directory for byemail """
    print("Initialize directory...")
    setting_tpl = path.join(path.realpath(path.dirname(__file__)), "settings_tpl.py")

    # Copy settings template
    shutil.copy(setting_tpl, path.join('.', 'settings.py'))

    print("Done.")


@begin.start
def run(version=False):
    """ byemail """
    if version:
        print(byemail.__version__)
        sys.exit(0)



