# -*- coding: utf-8 -*-

import codecs
from datetime import datetime
import email
import email.header
import email.utils
from email import charset
from email.mime.text import MIMEText
from email.utils import (make_msgid, getaddresses,
    parseaddr, formatdate, formataddr)
import re
from textwrap import TextWrapper

_quote_re = re.compile('((([>] ?)*( |$)))?')
_soft_re=re.compile(' $')

EMAIL_REGEX = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*" # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE # domain
)

def validEMail(value):
    return EMAIL_REGEX.match(value)


class EmailAddressList(object):
    """Email address list class
    
    The purpose of this class is to make it easier to work with email address
    containing strings.
    
    >>> a1 = EmailAddressList('Name 1 <1@foo.com>')
    >>> a2 = EmailAddressList('2@foo.com')
    >>> a3 = EmailAddressList('3@foo.com, 4@foo.com')
    >>> str(a1 + a3)
    'Name 1 <1@foo.com>, 3@foo.com, 4@foo.com'
    
    Duplicate entires are automatically removed:    
    >>> str(a1 + a2 + a2 + a1)
    'Name 1 <1@foo.com>, 2@foo.com'
    
    It is also easy to remove entries from a list:
    >>> str(a3 - '3@foo.com')
    '4@foo.com'
    """
    __slots__ = ('_addrs', '_lookup')
    
    def __init__(self, *args):
        self._lookup = {}
        self._addrs = []
        
        unicode_args = []
        #for arg in args:
        #     unicode_args.append(arg.decode('utf-8'))
        for name, email in getaddresses(map(str, args)):
        #for name, email in getaddresses(unicode_args):
            if email and not email in self._lookup:
                self._lookup[email] = name
                self._addrs.append((name, email))

    def __repr__(self):
        return '<%s %r>' % (type(self).__name__, self._addrs)

    def __str__(self):
        return ', '.join([formataddr(addr) for addr in self._addrs])

    def __getitem__(self, item):
        """
        >>> a = EmailAddressList('3@foo.com, Name 4 <4@foo.com>')
        >>> a[1]
        (u'Name 4', u'4@foo.com')
        """
        return self._addrs[item]

    def __len__(self):
        """
        >>> a = EmailAddressList('3@foo.com, Name 4 <4@foo.com>')
        >>> len(a)
        2
        """
        return len(self._addrs)
    
    def __iter__(self):
        """
        >>> a = EmailAddressList('3@foo.com, Name 4 <4@foo.com>')
        >>> list(a)
        [('', u'3@foo.com'), (u'Name 4', u'4@foo.com')]
        """
        return iter(self._addrs)

    def __contains__(self, other):
        """
        >>> addrs = EmailAddressList('a@example.com, b@example.com')
        >>> 'a@example.com' in addrs
        True
        >>> 'c@example.com' in addrs
        False
        """
        if not isinstance(other, EmailAddressList):
            other = EmailAddressList(other)
        for email in other._lookup.keys():
            if not email in self._lookup:
                return False
        return True
    
    def __add__(self, other):
        """
        >>> l1 = EmailAddressList('a@example.com, b@example.com')
        >>> l2 = EmailAddressList('a@example.com, c@example.com')
        >>> str(l1 + l2)
        'a@example.com, b@example.com, c@example.com'
        """
        return EmailAddressList(self, other)

    def __sub__(self, other):
        """
        >>> l1 = EmailAddressList('a@example.com, b@example.com')
        >>> l2 = EmailAddressList('a@example.com')
        >>> str(l1 - l2)
        'b@example.com'
        """
        new = EmailAddressList()
        if not isinstance(other, EmailAddressList):
            other = EmailAddressList(other)
        for name, email in self._addrs:
            if not email in other._lookup:
                new._lookup[email] = name
                new._addrs.append((name, email))
        return new

def parse_rfc2822_date(text):
    """Parse an rfc2822 date string into a datetime object."""
    t = email.utils.mktime_tz(email.utils.parsedate_tz(text))
    return datetime.utcfromtimestamp(t)
  
def encode_header(value, charset=None):
    """Encodes mail headers.

    If `value` is a list each list item will be encoded separately and
    returned as a comma separated list.
    If `value` is a tuple it will be interpreted as (name, email).
    """
    if isinstance(value, list):
        return ', \n\t'.join([encode_header(v, charset)
                              for v in value])
    elif isinstance(value, tuple):
        return '%s <%s>' % (email.header.Header(value[0], charset), value[1])
    else:
        return email.header.Header(value, charset)

def decode_header(text):
    """Decode a header value and return the value as a unicode string."""
    if not text:
        return text
    res = []
    for part, charset in email.header.decode_header(text):
        try:
            res.append(part.decode(charset or 'latin1', 'replace'))
        except LookupError:
            res.append(part.decode('utf-8', 'replace'))
    return ' '.join(res)

def unwrap_flowed(text):
    """Unwrap paragraphs that have been wrapped with "soft" new lines
    according to rfc2646.
    
    >>> unwrap_flowed('Foo \\nBar')
    'Foo Bar'
    >>> unwrap_flowed('Foo\\nBar')
    'Foo\\r\\nBar'
    >>> unwrap_flowed('> Foo \\n> Bar')
    '> Foo Bar'
    >>> unwrap_flowed('>> Foo \\n>> Bar')
    '>> Foo Bar'
    >>> unwrap_flowed('> > Foo \\n> > Bar')
    '> > Foo Bar'
    >>> unwrap_flowed('>> > Foo \\n>> > Bar')
    '>> > Foo Bar'
    """
    out = ''
    open_paragraph = False
    prev_level = -1
    for line in text.splitlines():
        indent = _quote_re.match(line).group(1) or ''
        level = indent.count('>')

        # This should never happen with properly format="flowed" text
        if level != prev_level:
            out.rstrip(' ')
            open_paragraph = False
        prev_level = level
        if open_paragraph:
            out += line[len(indent):]
        elif out:
            out += '\r\n' + line
        else:
            out = line
        open_paragraph = _soft_re.search(line)
    return out

def quote_text(text):
    """Quote text by prepending '>'-characters to each line"""
    lines = []
    for line in text.splitlines():
        if line.startswith('>'):
            line = '>' + line
        else:
            line = '> ' + line
        lines.append(line)
    return '\r\n'.join(lines)

def reflow_quoted_text(text, width=72):
    """Reflow text with 'soft' (SP CR LF) newlines according to rfc2646

    Text paragraphs containing 'soft' newlines are reflowed for a maximum
    line length of @width characters.
    Only non-quoted text is reflowed (Lines not starting with '>').
    
    >>> reflow_quoted_text('Foo \\nBar')
    'Foo Bar'
    >>> reflow_quoted_text('> Foo \\n> Bar')
    '> Foo \\r\\n> Bar'
    >>> reflow_quoted_text('> Foo \\nBar ')
    '> Foo \\r\\nBar'
    >>> reflow_quoted_text('> Foo\\n\\n> Bar')
    '> Foo\\r\\n\\r\\n> Bar'
    >>> reflow_quoted_text('> Foo \\n' \
                     'a b \\n' \
                     'c d e g h i j k l m\\n' \
                     '> Bar', width=10)
    '> Foo \\r\\na b c d e \\r\\ng h i j k \\r\\nl m\\r\\n> Bar'
    """
    wrapper = TextWrapper()
    wrapper.width = width
    lines = []
    paragraph = []
    for line in text.splitlines():
        if line.startswith('>'):
            if paragraph:
                lines.append(' \r\n'.join(wrapper.wrap(''.join(paragraph))))
                paragraph = []
            lines.append(line)
            continue
        paragraph.append(line)
        if not line.endswith(' '):
            if paragraph:
                lines.append(' \r\n'.join(wrapper.wrap(''.join(paragraph))))
                paragraph = []
    if paragraph:
        lines.append(' \r\n'.join(wrapper.wrap(''.join(paragraph))))
    return '\r\n'.join(lines)

def wrap_flowed(text, width=72):
    """Wrap long lines with 'soft' (SP CR LF) newlines according to rfc2646.
    
    >>> wrap_flowed('''foo bar foo bar ''' \
                    '''foo bar foo bar''', width=10)
    'foo bar \\r\\nfoo bar \\r\\nfoo bar \\r\\nfoo bar'
    """
    wrapper = TextWrapper()
    wrapper.width = width
    lines = []
    for line in text.splitlines():
        lines.append(' \r\n'.join(wrapper.wrap(line)))
    return '\r\n'.join(lines)
    

def decode_text_part(part):
    """Extract the payload from a text/plain mime part as a unicode string"""
    txt = part.get_payload(decode=True)
    charset = part.get_content_charset('latin1')
    # Make sure the charset is supported and fallback to 'ascii' if not
    try:
        codecs.lookup(charset)
    except LookupError:
        charset = 'ascii'
    return txt.decode(charset, 'replace')

def decode_text_plain_part(part):
    payload = decode_text_part(part)
    format = part.get_param('format', None)
    # We need to remove all trailing spaces from messages
    # that are not format="flowed" to avoid improper text
    # re-wrapping
    if format != 'flowed':
        payload = '\n'.join([line.rstrip(' ')
                             for line in payload.splitlines()])
    return payload
