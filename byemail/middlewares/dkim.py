import base64

import dkim
import magic

from byemail.conf import settings

async def sign(msg, from_addr, to_addrs):
    """ Adding DKIM signature to message """

    signature = gen_sign(msg)
    msg['DKIM-Signature'] = signature


async def verify(msg, from_addr, to_addrs):
    """ Verify DKIM signature """
    if not verify_sign(msg):
        raise 
    

def verify_sign(msg):
    return True


def gen_sign(msg):

    # TODO Open key one for all
    with open(settings.DKIM_CONFIG['private_key']) as key:
        private_key = key.read()

    identity = msg['From'].addresses[0].addr_spec.encode()

    # Generate message signature
    sig = dkim.sign(
        msg.as_bytes(), 
        settings.DKIM_CONFIG['selector'].encode(), 
        settings.DKIM_CONFIG['domain'].encode(), 
        private_key.encode(), 
        identity=identity,
        include_headers=[s.encode() for s in settings.DKIM_CONFIG['headers']],
        canonicalize=(b'relaxed',b'simple')
    )

    # Clean de generated signature
    sig = sig.decode().replace('\r\n ', '').replace('\r\n', '')

    # Add the DKIM-Signature
    signature = sig[len("DKIM-Signature: "):]

    return signature


def sign2(msg):
    # Not working for now but I don't know why
    import hashlib
    import base64
    import rsa

    res = OrderedDict([
        ('v', "1"),
        ('a', "rsa-sha256"),
        ('c', "simple/simple"),
        ('d', ""),
        ('i', ""),
        ('q', "dns/txt"),
        ('s', ""),
        ('h', []),
        ('bh', ""),
        ('b', ""),
    ])

    # TODO Open key one for all
    with open(settings.DKIM_CONFIG['private_key']) as key:
        private_key = key.read()
        '''.replace('\n', '')\
            .replace('-----BEGIN RSA PRIVATE KEY-----', '')\
            .replace('-----END RSA PRIVATE KEY-----', '')'''

    res['i'] = msg['From'].addresses[0].addr_spec
    res['d'] = settings.DKIM_CONFIG['domain']
    res['s'] = settings.DKIM_CONFIG['selector']
    res['h'] = " : ".join(settings.DKIM_CONFIG['headers'])

    body = msg.get_body(('html', 'plain',))
    #print(body.get_content())
    body_content = body.get_content()

    #body_content = """\n"""
    if body_content.endswith('\n'):
        body_content = body_content[:-1]

    body_content = body_content.replace('\n', '\r\n')
    #print(len(body_content))
    #print(repr(body_content))
    computed = base64.b64encode(hashlib.sha256(body_content.encode()).digest())
    #print(computed)
    res['bh'] = computed.decode()

    #assert computed == b"2jUSOH9NhtVGCQWNr9BrIAPreKQjO6Sn7XIkfJVOzv8="

    to_be_signed = ""
    for header in settings.DKIM_CONFIG['headers']:
        to_be_signed += "{}: {}\r\n".format(header, msg[header])

    to_be_signed += "DKIM-Signature: {}\r\n".format("; ".join([ "%s=%s" % v for v in res.items()]))
    print(repr(msg.as_bytes()))
    print(to_be_signed)

    #key = RSA.importKey(private_key)
    #print(key.size())
    #print(key.sign(to_be_signed.encode(), 10))

    print(rsa.sign(to_be_signed.encode(), private_key, 'SHA-1'))


    return "; ".join([ "%s=%s" % v for v in res.items()])