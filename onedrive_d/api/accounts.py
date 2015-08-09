"""
Account types of OneDrive API. Each account has its own session tokens and a managed REST client.
"""

import json
import time
from urllib import parse

import requests

from . import restapi
from ..common import logger_factory


def get_personal_account(client, code=None, uri=None):
    """
    Read account data from OneDrive Personal API.
    :param onedrive_d.api.clients.PersonalClient client: The underlying client object.
    :param str code: (Optional) The code to exchange for access token. Required if uri not set.
    :param str uri: (Optional) The landing URL of authentication process. Required if code not set.
    :rtype: PersonalAccount
    :raise ValueError: If code/uri is not set or cannot be used to get account information.
    """
    if uri is not None and '?' in uri:
        qs_dict = parse.parse_qs(uri.split('?')[1])
        if 'code' in qs_dict:
            code = qs_dict['code']
    if code is None:
        raise ValueError("Authorization code is not found.")
    params = {
        'client_id': client.client_id,
        'client_secret': client.client_secret,
        'redirect_uri': client.redirect_uri,
        'grant_type': 'authorization_code',
        'code': code,
    }
    response = requests.post(client.OAUTH_TOKEN_URI, data=params, proxies=client.proxies)
    if response.status_code != requests.codes.ok:
        raise ValueError('The authentication code is not valid.')
    account = PersonalAccount(client, response.json())
    return account


def get_business_account(client):
    """
    Read account data from OneDrive for Business API.
    :param onedrive_d.api.clients.BusinessClient client: The underlying OneDrive for Business client.
    :rtype: BusinessAccount
    """
    raise NotImplementedError("Support for OneDrive for Business is not implemented.")


class AccountTypes:
    PERSONAL = "personal"
    BUSINESS = "business"


class PersonalAccount:
    """Abstraction of a normal account type."""

    TYPE = AccountTypes.PERSONAL
    logger = logger_factory.get_logger('PersonalAccount')

    def __init__(self, client, session_info, expires_at=None):
        """
        :param onedrive_d.api.clients.PersonalClient | onedrive_d.api.clients.BusinessClient client: Parent client.
        :param dict[str, str | int] session_info: Raw dictionary of a response to access token request.
        :param int | None expires_at: A timestamp at which the tokens will expire.
        """
        self.client = client
        if expires_at is None:
            expires_at = time.time() + session_info['expires_in']
        self.expires_at = expires_at
        self.load_session(session_info)
        session = requests.Session()
        session.headers.update({'Authorization': 'Bearer ' + session_info['access_token']})
        self.session = restapi.ManagedRESTClient(
            session=session, account=self, proxies=client.proxies, net_mon=client.net_monitor)

    # noinspection PyAttributeOutsideInit
    def load_session(self, session_info):
        """Note that it is caller's responsibility to update expires_at."""
        self.access_token = session_info['access_token']
        self.refresh_token = session_info['refresh_token']
        self.token_type = session_info['token_type']
        self.scope = session_info['scope'].split(' ')

    def renew_tokens(self):
        params = {
            'client_id': self.client.client_id,
            'client_secret': self.client.client_secret,
            'redirect_uri': self.client.redirect_uri,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        request = self.session.post(self.client.OAUTH_TOKEN_URI, data=params,  auto_renew=False)
        session_info = request.json()
        self.expires_at = time.time() + session_info['expires_in']
        self.load_session(session_info)

    def sign_out(self):
        uri = '{0}?client_id={1}&redirect_uri={2}'.format(
            self.client.OAUTH_SIGN_OUT_URI, self.client.client_id, self.client.redirect_uri)
        self.session.get(uri)

    def dump(self):
        """
        :rtype str: A serialized JSON dictionary that can be passed back into __init__.
        """
        data = {
            'session_info': {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'scope': ' '.join(self.scope),
                'token_type': self.token_type
            },
            'expires_at': self.expires_at
        }
        return json.dumps(data)


class BusinessAccount:
    """Abstraction of an OneDrive Business account type."""

    TYPE = AccountTypes.BUSINESS

    def get_access_token(self):
        pass

    def get_refresh_token(self):
        pass

    def get_session_timeout(self):
        pass

    def refresh_token(self):
        pass

    def sign_out(self):
        pass

    def refresh_session(self):
        pass
