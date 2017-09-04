#!/usr/bin/env python
# coding: utf-8 -*-
#

# Import smtplib for the actual sending function
import smtplib
import sys

# Import the email modules we'll need
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders  
import email
import os
import codecs

if __name__ == "__main__":
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    
    for arg in sys.argv[1:]:
        print(arg)
        #message_file = codecs.open( arg, "r", "utf-8" )
        try:
            with open(arg, 'r') as in_file:
                msg = email.message_from_file(infile)
        except UnicodeDecodeError:
            with open(arg, 'r') as in_file:
                ff = file.read().decode('ISO-8859-1')
                msg = email.message_from_string(ff)
    
        me = "jrmi@localhost"
        you = "jrmi@localhost"
        #msg['From'] = me
        msg['To'] = you
        s = smtplib.SMTP("::1", 8025, "localhost", 10)
        s.set_debuglevel(0)
        s.sendmail(me, [you], msg.as_string())
        
        s.quit()