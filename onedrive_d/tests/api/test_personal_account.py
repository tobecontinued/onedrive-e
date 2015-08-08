import json
import re
import unittest

import requests
import requests_mock

from onedrive_d.api import accounts
from onedrive_d.api import clients
from onedrive_d.tests.api.account_factory import personal_account_data as data
from onedrive_d.tests.api.account_factory import get_sample_personal_account as get_sample_account
from onedrive_d.tests.api.client_factory import get_sample_personal_client as get_sample_client


class TestPersonalAccount(unittest.TestCase):
    # Sample data acquired from
    # https://github.com/OneDrive/onedrive-api-docs/blob/master/auth/msa_oauth.md

    def assert_account(self, account):
        """
        :param onedrive_d.api.accounts.PersonalAccount account:
        """
        self.assertIsInstance(account, accounts.PersonalAccount)
        self.assertEqual(data['access_token'], account.access_token)
        self.assertEqual(data['refresh_token'], account.refresh_token)
        self.assertEqual(data['token_type'], account.token_type)
        self.assertEqual(2, len(account.scope))
        self.assertIn('wl.basic', account.scope)
        self.assertIn('onedrive.readwrite', account.scope)
        self.assertGreater(account.expires_at, data['expires_in'])

    def test_get_account_fail_nocode(self):
        client = get_sample_client()
        self.assertRaises(ValueError, accounts.get_personal_account, client, uri='http://foo/bar?error=123')

    def test_get_account_fail_badcode(self):
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                self.assertIn('code=123', request.text)
                context.status_code = requests.codes.bad
                return {
                    'error': 'dummy error',
                    'error_description': 'dummy description'
                }
            mock.post(re.compile('//login\.live\.com\.*'), json=callback)
            client = get_sample_client()
            self.assertRaises(ValueError, accounts.get_personal_account, client, uri='http://foo/bar?error=123')

    def test_get_account_by_code(self):
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                self.assertIn('code=123', request.text)
                return data
            mock.post(re.compile('//login\.live\.com\.*'), json=callback, status_code=requests.codes.ok)
            client = get_sample_client()
            account = accounts.get_personal_account(client, code='123')
            self.assert_account(account)

    def test_get_account_by_uri(self):
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                self.assertIn('code=123', request.text)
                return data

            mock.post(re.compile('//login\.live\.com\.*'), json=callback, status_code=requests.codes.ok)
            client = get_sample_client()
            account = accounts.get_personal_account(client, uri='http://foo/bar?code=123')
            self.assert_account(account)

    def test_parse_expire_time(self):
        expires_at = 1234
        client = clients.PersonalClient('dummy_client_id', 'dummy_secret')
        account = accounts.PersonalAccount(client, data, expires_at)
        self.assertEqual(expires_at, account.expires_at)

    def test_load_session(self):
        account = get_sample_account()
        new_data = {
            'access_token': 'whatever',
            'expires_in': 7200,
            'refresh_token': 'whatever_refresh',
            'scope': 'a b c',
            'token_type': 'bearer2',
        }
        account.load_session(new_data)
        self.assertEqual(new_data['access_token'], account.access_token)
        self.assertEqual(new_data['refresh_token'], account.refresh_token)
        self.assertEqual(new_data['token_type'], account.token_type)
        self.assertEqual(3, len(account.scope))
        self.assertIn('a', account.scope)
        self.assertIn('b', account.scope)
        self.assertIn('c', account.scope)

    def test_dump(self):
        account = get_sample_account()
        dump = account.dump()
        self.assertIsInstance(dump, str)
        data = json.loads(dump)
        data['client'] = account.client
        account_restore = accounts.PersonalAccount(**data)
        self.assertEqual(account.access_token, account_restore.access_token)
        self.assertEqual(account.refresh_token, account_restore.refresh_token)
        self.assertEqual(account.expires_at, account_restore.expires_at)


if __name__ == '__main__':
    unittest.main()
