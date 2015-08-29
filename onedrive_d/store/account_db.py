__author__ = 'xb'

import atexit
import sqlite3

from onedrive_d import get_content
from onedrive_d.api import accounts
from onedrive_d.api import resources
from onedrive_d.common import logger_factory


class AccountStorage:
    """
    A SQLite-based storage layer for account and drive objects.
    """

    logger = logger_factory.get_logger('AccountStorage')

    def __init__(self, db_path, personal_client=None, business_client=None):
        self._conn = sqlite3.connect(db_path, isolation_level=None)
        self._cursor = self._conn.cursor()
        self._cursor.execute(get_content('onedrive_accounts.sql'))
        self._conn.commit()
        self.personal_client = personal_client
        self.business_client = business_client
        self._all_accounts = {}
        atexit.register(self.close)

    def parse_account_type(self, account_type):
        """
        :param str account_type:
        :return onedrive_d.api.accounts.PersonalAccount | onedrive_d.accounts.accounts.BusinessAccount:
        """
        if account_type == accounts.AccountTypes.PERSONAL:
            return accounts.PersonalAccount, self.personal_client
        else:
            return accounts.BusinessAccount, self.business_client

    def deserialize_account_row(self, account_id, account_type, account_dump, profile_dump, container):
        account_cls, client = self.parse_account_type(account_type)
        if client is None:
            self.logger.warning('Account %s was not loaded since no client of that type provided.', account_id)
            return
        try:
            account = account_cls.load(client, account_dump)
            container[(account_id, account_type)] = account
        except ValueError as e:
            self.logger.warning('Failed to deserialize account %s: %s', account_id, e)
        else:
            try:
                profile = resources.UserProfile.load(profile_dump)
            except ValueError as e:
                self.logger.warning('Failed to deserialize user profile for account %s: %s', account_id, e)
                profile = account.profile
            account.profile = profile

    def get_all_accounts(self):
        self._conn.commit()
        q = self._cursor.execute('SELECT account_id, account_type, account_dump, profile_dump FROM accounts')
        for row in q.fetchall():
            account_id, account_type, account_dump, profile_dump = row
            self.deserialize_account_row(account_id, account_type, account_dump, profile_dump, self._all_accounts)
        return self._all_accounts

    def get_account(self, account_id, account_type):
        key = (account_id, account_type)
        if key in self._all_accounts:
            return self._all_accounts[key]
        else:
            return None

    def add_account(self, account):
        profile = account.profile
        if (profile.user_id, account.TYPE) not in self._all_accounts:
            self._all_accounts[(profile.user_id, account.TYPE)] = account

    def insert_record(self, account):
        profile = account.profile
        params = (profile.user_id, account.TYPE, account.dump(), profile.dump())
        self._cursor.execute(
            'INSERT OR REPLACE INTO accounts (account_id, account_type, account_dump, profile_dump) '
            'VALUES (?, ?, ?, ?)', params)

    def delete_account(self, account):
        key = (account.profile.user_id, account.TYPE)
        del self._all_accounts[key]
        self._cursor.execute('DELETE FROM accounts WHERE account_id=? AND account_type=?', key)

    def close(self):
        # Write all data back to database
        self.logger.info('Writing account information back to storage...')
        for account_key, account in self._all_accounts.items():
            self.insert_record(account)
        self._conn.commit()
        # Close database connection
        self.logger.info('Closing account storage...')
        self._cursor.close()
        self._conn.close()
        self.logger.info('Account storage was closed.')
