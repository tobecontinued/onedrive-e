import unittest

import requests
import requests_mock

from onedrive_d.api import drives
from onedrive_d.api import facets
from onedrive_d.tests import get_data
from onedrive_d.tests.api.account_factory import get_sample_personal_account


class TestDriveRoot(unittest.TestCase):
    def setUp(self):
        self.account = get_sample_personal_account()
        self.root = drives.DriveRoot(self.account)

    def test_get_all_drives(self):
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                all_drives = [get_data('drive.json'), get_data('drive.json')]
                i = 0
                for x in all_drives:
                    x['id'] = str(i)
                    i = i + 1
                context.status_code = requests.codes.ok
                return {'value': all_drives}

            mock.get(self.account.client.API_URI + '/drives', json=callback)
            all_drives = self.root.get_all_drives()
            all_ids = [str(i) for i in range(0, 2)]
            for i, x in all_drives.items():
                self.assertIn(i, all_ids)
                self.assertIsInstance(x, drives.DriveObject)
                all_ids.remove(i)
            self.assertEqual(0, len(all_ids))


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
