#!/usr/bin/env python

import sys
import email
import codecs

from email import policy
from email.parser import BytesParser


def mail_from_file(mail_path):

    with open(arg, "rb") as in_file:
        #import ipdb; ipdb.set_trace()
        ff = in_file.read()

    msg = BytesParser(policy=policy.default).parsebytes(ff)

    return msg


if __name__ == "__main__":
    from smtplib import SMTP as Client

    client = Client('localhost', 8025)

    for arg in sys.argv:
        print(f"Sending {arg}")
        try:
            msg = mail_from_file(arg)
            r = client.sendmail('from@localhost', ['to@localhost'], msg.as_bytes())
        except:
            print(f"EEEEEE - Fail to send {arg}")