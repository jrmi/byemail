from tinydb import TinyDB, Query

from leefmail.conf import settings

class Account():
    def __init__(self, id, name, password, accept, address):
        self.id = id
        self.name = name
        self.password = password
        self.accept = accept
        self.session = {}
        self.address = address

    def check_credentials(self, credentials):
        return credentials['password'] == self.password

    def match_address(self, address):
        # Simple version for now but planning regex
        for matcher in self.accept:
            if address.endswith(matcher):
                return True
        return False

    def get_session(self):
        return self.session

    def to_json(self):
        result = dict(self.__dict__)
        del result['password']
        return result

    def __str__(self):
        return "Account(%s)" % self.name


class AccountManager():
    """ Account manager """
    def __init__(self):
        # Load all accounts from configuration
        self.accounts = self.load_accounts()
        print(self.accounts)

    def load_accounts(self):
        result = {}
        for settings_account in settings.ACCOUNTS:
            account = Account(**{
                'id': settings_account['name'],
                'name': settings_account['name'],
                'password': settings_account['password'],
                'accept': settings_account['accept'],
                'address': settings_account['address'],
            })
            result[settings_account['name']] = account

        return result

    def get(self, name):
        return self.accounts.get(name)

    def authenticate(self, credentials):
        account = self.get(credentials['name'])

        if account and account.check_credentials(credentials):
            return account
        return None

    def get_from_token(self, token):
        return

    def is_local_address(self, address):
        return self.get_account_for_address(address) is not None

    def get_account_for_address(self, address):
        for name, account in self.accounts.items():
            if account.match_address(address):
                return account

        return None

account_manager = AccountManager()
