""" Configuration file """
import os


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

STORAGE = {
    "backend": "byemail.storage.tinydb.Backend",
    "datadir": "data/"
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
