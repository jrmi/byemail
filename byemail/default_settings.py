""" Configuration file """
import os

# Account list
# example :
# {
#     'name': 'myname', # For login
#     'password': 'test', # Password
#     'address': 'my super mail <mysupermail@example.com>' # The from address
#     'accept': ['@example.com'], # All accepted email address suffixes
# }
ACCOUNTS = []

DEBUG = True

DATADIR = "data/"

DKIM_CONFIG = {
    'private_key': os.path.join(DATADIR, 'dkimprivatekey.pem'),
    'public_key': os.path.join(DATADIR, 'dkimpublickey.pem'),
    'selector': 'dkim',
    'domain': 'example.com',
    'headers': ['From', 'To', 'Subject', 'Date', 'Message-Id']
}

HTTP_CONF = {
    'host': 'localhost',
    'port': 8000
}

SMTP_CONF = {
    'hostname': 'localhost', # None for default
    'port': 8025,
    'ssl_context': None, # For enabling SSL provide context
}

MTA_MIDDLEWARES = [
    # Next middleware not working yet
    # 'byemail.middlewares.dkim.sign'
]

INCOMING_MIDDLEWARES = [
    # Next middleware not working yet
    # 'byemail.middlewares.dkim.verify'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },

    'loggers': {
        # root loggers
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
    }
}
