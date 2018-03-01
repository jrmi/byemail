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

DATADIR = "data/"

HTTP_CONF = {
    'host': 'localhost',
    'port': 8000
}

SMTP_CONF = {
    'hostname': 'localhost', # None for default
    'port': 8025,
    'ssl_context': None, # For enabling SSL provide context
}

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
