#!/usr/bin/env python
# coding: utf-8 -*-
#
from smtpd import SMTPServer

import asyncore
import asynchat
import traceback

from leefMail.mySMTP.models import RawMessage, new_raw_message
import leefMail.webmail.models 

class mySMTP (SMTPServer):
    def process_message (self, peer, mailfrom, rcpttos, data):
        try:
            print rcpttos
            raw_message = RawMessage.store_message(data,rcpttos)
            new_raw_message.send(raw_message)
        except Exception, e:
            # TODO En cas d'erreur on enregistre le fichier...
            traceback.print_exc()
            raise

if __name__ == "__main__":
    test = mySMTP(("192.168.1.5",8025) ,("smtp.neuf.fr",25))
    try:
        asyncore.loop ()
    except KeyboardInterrupt:
        pass
  
