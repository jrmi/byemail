#!/usr/bin/env python
# coding: utf-8 -*-
#

from django.core.files.base import ContentFile
from leefMail.smtp.util.msg import MessageRenderer


from smtpd import SMTPServer

import email
import uuid
import asyncore
import asynchat
import os
import sys
import traceback
import errno
import mimetypes
from datetime import datetime

from leefMail.webmail.models import Message, Attachment, Tag

messRend = MessageRenderer()

class persoSMTP (SMTPServer):
    def process_message (self, peer, mailfrom, rcpttos, data):
        try:
            msg = messRend.process_msg(email.message_from_string(data))
            print(msg['head'])
            #print(msg['parts'])
            #print(msg['attachments'])
            message = Message()
            message.subject = msg['head']['subject']
            message.mail_to = msg['head']['to']
            message.mail_from = msg['head']['from']
            
            # Si pas de date on met la date de reception
            if(msg['head']['date']):
                message.send_date = msg['head']['date']
            else:
                message.send_date = datetime.now()
                
            message.content = '\n'.join(msg['parts'])
            msg_filename = uuid.uuid4()
            message.raw_message.save(str(msg_filename),ContentFile(data), False )
            
            message.save()

            for attach in msg['attachments']:
                content_type = attach['content_type']
                # TODO Gerer les mails en piece jointe
                if(content_type != 'message/rfc822'):
                    attachment = Attachment()
                    attachment.mime_type = content_type
                    attachment.filename = attach['filename']
                    attachment.content_id = attach['content_id']
                    attachment.description = attach['description']
                    attachment.message = message
                    attachment.save()

            for tag in Tag.objects.filter(default = True).all():
                message.tags.add(tag)
        except Exception, e:
            # TODO En cas d'erreur on enregistre le fichier...
            print(e)
            print(traceback.print_exc())
            raise



if __name__ == "__main__":
    test = persoSMTP(("192.168.1.5",8025) ,("smtp.neuf.fr",25))
    try:
        asyncore.loop ()
    except KeyboardInterrupt:
        pass
  
        
        
        """
            counter = 1
            for part in msg.walk():
                # multipart/* are just containers
                if part.get_content_maintype() == 'multipart':
                    continue
                # Applications should really sanitize the given filename so that an
                # email message can't be used to overwrite important files
                filename = part.get_filename()
                print(filename)
                if not filename:
                    ext = mimetypes.guess_extension(part.get_content_type())
                    if not ext:
                        # Use a generic bag-of-bits extension
                        ext = '.bin'
                    filename = 'part-%03d%s' % (counter, ext)
                counter += 1
                fp = open(os.path.join(".", filename), 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()"""
