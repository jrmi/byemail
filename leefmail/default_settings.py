""" Configuration file """

ACCEPT = ['@localhost']

HTTP_CONF = {
    'host': 'localhost',
    'port': 8000
}

SMTP_CONF = {
    'hostname': None, # None for default
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
