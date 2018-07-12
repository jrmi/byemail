from email import policy
from email.parser import BytesParser

class objectview(object):
    def __init__(self, d):
        self.__dict__ = d
