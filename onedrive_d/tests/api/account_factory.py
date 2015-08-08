from onedrive_d.api import accounts
from onedrive_d.tests import get_data

personal_account_data = get_data('personal_access_token.json')


def get_sample_personal_account(client=None):
    if client is None:
        from . import client_factory
        client = client_factory.get_sample_personal_client()
    account = accounts.PersonalAccount(client, personal_account_data)
    return account
