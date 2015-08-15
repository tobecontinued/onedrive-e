from onedrive_d.api import accounts
from onedrive_d.api import resources
from onedrive_d.tests import get_data

PERSONAL_ACCOUNT_DATA = get_data('personal_access_token.json')
USER_PROFILE_DATA = get_data('user_profile.json')

def get_sample_personal_account(client=None):
    if client is None:
        from . import client_factory
        client = client_factory.get_sample_personal_client()
    account = accounts.PersonalAccount(client, PERSONAL_ACCOUNT_DATA)
    account.profile = resources.UserProfile(USER_PROFILE_DATA)
    return account
