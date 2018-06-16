""" Configuration file """
import os

ACCOUNTS = []

DEBUG = False

STORAGE = {
    "backend": "byemail.storage.tinydb.Backend",
    "datadir": "data/"
}

DKIM_CONFIG = {
    'private_key': 'dkimprivatekey.pem',
    'public_key': 'dkimpublickey.pem',
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

OUTGOING_MIDDLEWARES = [
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
