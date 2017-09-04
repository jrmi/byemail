
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