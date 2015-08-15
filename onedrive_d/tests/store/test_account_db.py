__author__ = 'xb'

import atexit
import unittest

from requests import codes
from requests_mock import Mocker

from onedrive_d.api import accounts
from onedrive_d.store.account_db import AccountStorage
from onedrive_d.tests import get_data
from onedrive_d.tests.mocks import mock_atexit
from onedrive_d.tests.api.account_factory import get_sample_personal_account

atexit.register = mock_atexit.register


def get_sample_account_storage(personal_client=None, business_client=None):
    return AccountStorage(
        ':memory:',
        personal_client=personal_client,
        business_client=business_client)


class TestAccountStorage(unittest.TestCase):
    def setUp(self):
        self.personal_account = get_sample_personal_account()
        self.account_store = get_sample_account_storage(self.personal_account.client, None)

    def assert_get_account(self, account_id, account_type, what):
        q = self.account_store.get_account(account_id, account_type)
        self.assertIs(q, what)

    def test_add_get(self):
        self.account_store.add_account(self.personal_account)
        self.assert_get_account(
            self.personal_account.profile.user_id,
            self.personal_account.TYPE,
            self.personal_account)

    def test_get_none(self):
        self.assert_get_account(
            self.personal_account.profile.user_id,
            self.personal_account.TYPE,
            None)

    def test_parse_account_type(self):
        self.assertEqual(self.account_store.parse_account_type(accounts.AccountTypes.PERSONAL),
                         (accounts.PersonalAccount, self.personal_account.client))
        self.assertEqual(self.account_store.parse_account_type(accounts.AccountTypes.BUSINESS),
                         (accounts.BusinessAccount, None))

    def test_deserialize_account_row(self):
        d = {}
        self.account_store.deserialize_account_row(
            self.personal_account.profile.user_id,
            self.personal_account.TYPE,
            self.personal_account.dump(),
            self.personal_account.profile.dump(),
            d)
        self.assertEqual(1, len(d))

    def test_deserialize_account_no_client(self):
        d = {}
        self.account_store.deserialize_account_row('foo', accounts.AccountTypes.BUSINESS, None, None, d)
        self.assertEqual(0, len(d))

    def test_deserialize_account_bad_account_dump(self):
        d = {}
        self.account_store.deserialize_account_row(
            self.personal_account.profile.user_id,
            self.personal_account.TYPE,
            self.personal_account.dump() + '.',
            self.personal_account.profile.dump(),
            d)
        self.assertEqual(0, len(d))

    @Mocker()
    def test_deserialize_account_bad_profile(self, mock):
        d = {}
        mock.get('https://apis.live.net/v5.0/me', json=get_data('user_profile.json'), status_code=codes.ok)
        self.account_store.deserialize_account_row(
            self.personal_account.profile.user_id,
            self.personal_account.TYPE,
            self.personal_account.dump(),
            self.personal_account.profile.dump() + '.',
            d)
        self.assertEqual(1, len(d))

    def test_get_all_accounts(self):
        self.account_store.insert_record(self.personal_account)
        all_accounts = self.account_store.get_all_accounts()
        self.assertIsInstance(all_accounts, dict)
        self.assertEqual(1, len(all_accounts))

    def tearDown(self):
        self.account_store.close()


if __name__ == '__main__':
    unittest.main()
