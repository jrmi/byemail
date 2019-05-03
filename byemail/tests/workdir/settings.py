""" Test configuration file """
from byemail.default_settings import *

ACCOUNTS = [
    {
        "name": "test",
        "password": "test_pass",
        "accept": ["@anything.com"],
        "address": "Test <test@anything.com>",
    }
]

STORAGE = {
    "backend": "byemail.storage.sqldb.Backend",
    "config": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": ":memory:"},
        }
    },
}

