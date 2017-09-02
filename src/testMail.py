#!/usr/bin/env python
# coding: utf-8 -*-
#

# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders  
import os

if __name__ == "__main__":
    msg = MIMEMultipart() 
    
    me = "jrmi@free.fr"
    you = "jrmi@jrmi.homelinux.net"
    msg['Subject'] = 'Message de test'
    msg['From'] = me
    msg['To'] = you
    
    msg.attach(MIMEText("Ceci est un message de test"))
    
    files = ["/home/jeremie/radios.sh","/home/jeremie/tvshows.m3u"]
    for f in files:  
        part = MIMEBase('application', 'octet-stream')  
        part.set_payload(open(f, 'rb').read())  
        Encoders.encode_base64(part)  
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))  
        msg.attach(part)  
    
    
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP("192.168.1.5",8025,"jrmi.homelinux.net", 10)
    s.set_debuglevel(1)
    s.sendmail(me, [you], msg.as_string())
    s.quit()
