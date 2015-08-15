__author__ = 'xb'

import atexit
import unittest

from requests import codes

from requests_mock import Mocker

from onedrive_d.api import accounts
from onedrive_d.store.account_db import AccountStorage
from onedrive_d.tests import get_data
from onedrive_d.tests.api.account_factory import get_sample_personal_account


def mock_atexit_register(cls, **kwargs):
    return


atexit.register = mock_atexit_register


class TestAccountStorage(unittest.TestCase):
    def setUp(self):
        self.personal_account = get_sample_personal_account()
        self.account_store = AccountStorage(
            ':memory:',
            personal_client=self.personal_account.client,
            business_client=None)

    def assert_get_account(self, account_id, account_type, what):
        q = self.account_store.get_account(account_id, account_type)
        self.assertTrue(q is what)

    def test_add_get(self):
        self.account_store.add_account(self.personal_account)
        self.assert_get_account(
            self.personal_account.profile.user_id,
            self.personal_account.TYPE,
            self.personal_account)
        self.account_store.close()

    def test_get_none(self):
        self.assert_get_account(
            self.personal_account.profile.user_id,
            self.personal_account.TYPE,
            None)
        self.account_store.close()

    def test_parse_account_type(self):
        self.assertEqual(self.account_store.parse_account_type(accounts.AccountTypes.PERSONAL),
                         (accounts.PersonalAccount, self.personal_account.client))
        self.assertEqual(self.account_store.parse_account_type(accounts.AccountTypes.BUSINESS),
                         (accounts.BusinessAccount, None))
        self.account_store.close()

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
        all_accounts = self.account_store.get_all_accounts(None)
        self.assertIsInstance(all_accounts, dict)
        self.assertEqual(1, len(all_accounts))


if __name__ == '__main__':
    unittest.main()
