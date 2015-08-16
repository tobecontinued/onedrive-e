__author__ = 'xb'

import unittest

from onedrive_d.api import drives
from onedrive_d.common.drive_config import DriveConfig
from onedrive_d.store import drives_db
from onedrive_d.tests import get_data
from onedrive_d.tests.api.account_factory import get_sample_personal_account
from onedrive_d.tests.mocks import mock_atexit
from onedrive_d.tests.mocks import mock_logger
from onedrive_d.tests.store.test_account_db import get_sample_account_storage

mock_atexit.mock_register()
mock_logger.mock_loggers()


class TestDriveStorage(unittest.TestCase):
    def setUp(self):
        self.personal_account = get_sample_personal_account()
        self.account_store = get_sample_account_storage(self.personal_account.client, None)
        self.account_store.add_account(self.personal_account)
        self.drives_store = drives_db.DriveStorage(':memory:', self.account_store)
        self.drive_root = self.drives_store.get_drive_root(
            self.personal_account.profile.user_id, self.personal_account.TYPE)

    def test_get_drive_root(self):
        self.assertIsInstance(self.drive_root, drives.DriveRoot)
        self.assertIs(self.drive_root.account, self.personal_account)

    def test_get_all_drives(self):
        drive = drives.DriveObject(self.drive_root, get_data('drive.json'), DriveConfig.default_config())
        self.drives_store.add_record(drive)
        for k, drive_value in self.drives_store.get_all_drives().items():
            drive_id, account_id, account_type = k
            self.assertEqual(drive_id, drive_value.drive_id)
            self.assertEqual(drive.drive_id, drive_value.drive_id)
            self.assertEqual(drive.config.local_root, drive_value.config.local_root)

    def test_assemble_drive_error(self):
        d = {}
        drive = drives.DriveObject(self.drive_root, get_data('drive.json'), DriveConfig.default_config())
        rows = [
            ('did', 'aid', 'at', drive.dump() + '.'),
            (drive.drive_id, self.personal_account.profile.user_id, self.personal_account.TYPE, drive.dump() + '.')
        ]
        for r in rows:
            self.drives_store.assemble_drive_record(r, d)
            self.assertEqual(0, len(d), str(r))

    def tearDown(self):
        self.drives_store.close()
        self.account_store.close()


if __name__ == '__main__':
    unittest.main()
