""" Configuration file """
import os

BASEDIR = os.path.dirname(__file__)
DATADIR = os.path.join(BASEDIR, "data")

DOMAIN = "http://localhost:8080"  # Domain to serve content

ACCOUNTS = [
    # Account list
    # example :
    # {
    #     'name': 'myname', # For login
    #     'password': 'test', # Password
    #     'address': 'my super mail <mysupermail@example.com>', # The from address
    #     'accept': ['@example.com'], # All accepted email address suffixes
    # }
]

DEBUG = False

STORAGE = {"backend": "byemail.storage.sqldb.Backend", "uri": "sqlite://db.sqlite"}

HTTP_CONF = {"host": "localhost", "port": 8000}

SMTP_CONF = {
    "host": "localhost",  # None for default
    "port": 8025,
    "ssl": None,  # For enabling SSL provide context
}

OUTGOING_MIDDLEWARES = [
    # Next middleware not working yet
    # 'byemail.middlewares.dkim.sign'
]

INCOMING_MIDDLEWARES = [
    # Next middleware not working yet
    # 'byemail.middlewares.dkim.verify'
]

VAPID_PUBLIC_KEY = "vapid_public_key.pem"
VAPID_PRIVATE_KEY = "vapid_private_key.pem"
VAPID_CLAIMS = {"sub": "mailto:youremail"}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(threadName)s %(name)s %(module)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        # root loggers
        "": {"level": "DEBUG", "handlers": ["console"]},
        "mail.log": {"level": "INFO"},
        "asyncio": {"level": "WARNING"},
        "aiosqlite": {"level": "INFO"},
        "db_client": {"level": "INFO"},
    },
}

