# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://posterity.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://posterity.edgewall.org/log/.

import re
import email

from mailutils import decode_header, decode_text_part, \
    decode_text_plain_part, parse_rfc2822_date

missing = object()
href_re = re.compile('(.*)(http://[^> ]+)(.*)')

quote_re = re.compile('((?:[>] ?)*)(.*)')

class MessageRenderer(object):
    """Parses a rfc822 message into a python structure.

    A message is represented by dictionary of the following format:
    {
      'head': dict(subject=, from=, to=, cc=, bcc, date),
      'parts': [part1, part2, ...]
      'attachments': [attachment1, attachment2, ...]
    }
    `parts` is a list of messages mime parts that can be inlined into
    the message, usually text/plain and text/html.
    
    `attachments` is a list of dictionaries of the following format:
    dict(content_type=, content_id=, filename=, description=).
    If the attachments is a rfc822 message `content_type` is set to
    'message/rfc822' and the rest of the dictionary is identical to the
    message representation described above.
    
    """
    def render(self, msg):
        part = email.message_from_string(msg.payload)
        return self.process_msg(part)

    def process_msg(self, part):
        head = {}
        parts = []
        attachments = []
        head['subject'] = decode_header(part['Subject'])
        head['from'] = decode_header(part['From'])
        head['to'] = decode_header(part['To'])
        head['cc'] = decode_header(part['CC'])
        head['bcc'] = decode_header(part['BCC'])
        head['reply_to'] = decode_header(part['Reply-To'])
        head['organization'] = decode_header(part['Organization'])
        try:
            head['date'] = parse_rfc2822_date(part['Date'])
        except:
            head['date'] = None
        self.process_part(part, parts, attachments, ignore_msg=True)
        return dict(head=head, parts=parts, attachments=attachments,
                    content_type='message/rfc822')

    def process_part(self, part, parts, attachments, ignore_msg=False):
        content_type = part.get_content_type()
        attachment = part.get_param('attachment', missing, 
                                    'Content-Disposition')
        if content_type == 'message/rfc822' :
            if (not ignore_msg):
                for msg in part.get_payload():
                    attachments.append(self.process_msg(msg))
            return True
            
        if part.is_multipart():
            # In case of a multipart/alternative multipart all parts
            # are syntactically identical but semantically different.
            # This means that we should only inline one version of the
            # information.
            if content_type == 'multipart/alternative':
                for p in reversed(part.get_payload()):
                    if self.process_part(p, parts, attachments):
                        return True 
            else:
                for p in part.get_payload():
                    self.process_part(p, parts, attachments)
            return True
        success = False
        if content_type == 'text/html' and attachment is missing:
            #data = self.render_text_html(part)
            data = decode_text_part(part)
            if data:
                parts.append(data)
                success = True
        elif content_type.startswith('text/') and attachment is missing:
            #parts.append(self.render_text_plain(part))

            parts.append(decode_text_plain_part(part))
            success = True
        # Is it an attachment?
        filename = part.get_filename(None)
        if filename:
            content_id = part.get('Content-Id', '').strip('<>')
            description = decode_header(part.get('content-description',''))
            attachments.append(dict(filename=filename, 
                                    content_id=content_id,
                                    content_type=content_type,
                                    description=description))
            success = True
        return success


class EmailFilter(object):
    """Rename unwanted elements from html emails
    
    Most html emails contains elements that have to be renamed to something
    safer before they can be inlined into the Posterity message view.
    
    This filter currently rename html, head and body elements to div.
    
    >>> from genshi.input import HTML
    >>> stream = HTML('<html><head/><body>foo</body></html>')
    >>> stream = stream | EmailFilter()
    >>> stream.render()
    '<div><div/><div>foo</div></div>'
    """
    def __call__(self, stream):
        for kind, data, pos in stream:
            if kind is START:
                tag, attrib = data
                if tag.lower() in ['html', 'head', 'body']:
                    data = QName('div'), attrib
            if kind is END:
                if data.lower() in ['html', 'head', 'body']:
                    data = QName('div')
            yield kind, data, pos


