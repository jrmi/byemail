""" Test configuration file """
from byemail.default_settings import *

ACCOUNTS = [{
    'name': 'test',
    'password': 'test_pass',
    'accept': ['@anything.com'],
    'address': 'Test <test@anything.com>'
}]