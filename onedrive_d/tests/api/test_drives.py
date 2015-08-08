import unittest

from onedrive_d.api import drives
from onedrive_d.api import facets
from onedrive_d.tests import get_data
from onedrive_d.tests.api.account_factory import get_sample_personal_account


class TestDriveObject(unittest.TestCase):
    def test_parse(self):
        account = get_sample_personal_account()
        root = drives.DriveRoot(account)
        drive_data = get_data('drive.json')
        drive = drives.DriveObject(root=root, data=drive_data)
        self.assertEqual(drive_data['id'], drive.id)
        self.assertEqual(drive_data['driveType'], drive.type)
        self.assertIsInstance(drive.quota, facets.QuotaFacet)


if __name__ == '__main__':
    unittest.main()
