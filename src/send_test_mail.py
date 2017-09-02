#!/bin/env python

import sys
import email
import codecs

def mail_from_file(mail_path):
    try:
        with open(arg, "r") as in_file:
            msg = email.message_from_file(in_file)
    except UnicodeDecodeError:
        with codecs.open(arg, 'r', 'ISO-8859-1') as in_file:
            ff = in_file.read()
            #ff = ff.decode('ISO-8859-1')
            #ff = ff.encode('utf-8')
            msg = email.message_from_string(ff)

    return msg


if __name__ == "__main__":
    from smtplib import SMTP as Client

    client = Client('::1', 8025)
    '''r = client.sendmail('test@localhost', ['toto@localhost'], """
    From: Anne Person <anne@example.com>
    To: Bart Person <bart@example.com>
    Subject: A test
    Message-ID: <ant>

    Hi Bart, this is Anne.
    """)'''

    for arg in sys.argv[1:]:
        print(arg)
        msg = mail_from_file(arg)
        st = msg.as_string()

        r = client.sendmail('test@localhost', ['toto@localhost'], st.encode('utf-8'))
        

