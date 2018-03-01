#!/usr/bin/env python

import sys
import email
import codecs

import chardet

from email import policy
from email.parser import BytesParser


def decode(s, encodings=('utf8', 'iso-8859-1', 'iso-8859-2', 'latin1')):
    detected = chardet.detect(s)
    encodings = [detected['encoding']] + list(encodings)
    for encoding in encodings:
        try:
            success = s.decode(encoding)
            print('Decoded with %s' % encoding)
            return success
        except UnicodeDecodeError:
            pass
    return s.decode('ascii', 'ignore')

def mail_from_file(mail_path):

    with open(arg, "rb") as in_file:
        #import ipdb; ipdb.set_trace()
        ff = in_file.read()

    decoded = decode(ff)
    msg = BytesParser(policy=policy.default).parsebytes(decoded.encode('utf-8'))

    return msg


if __name__ == "__main__":
    from smtplib import SMTP as Client

    client = Client('localhost', 8025)

    for arg in sys.argv[1:]:
        print(arg)
        msg = mail_from_file(arg)
        #import ipdb; ipdb.set_trace()

        try:
           msg.as_string().encode('utf-8')
        except:
            print('File %r failed to convert' % arg)
            #import ipdb; ipdb.set_trace()
        else:
            r = client.sendmail('from@localhost', ['to@localhost'], msg.as_string().encode('utf-8'))

        

