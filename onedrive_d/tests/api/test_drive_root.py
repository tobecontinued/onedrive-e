import unittest

import requests_mock
from requests import codes

from onedrive_d.api import drives
from onedrive_d.tests import get_data
from onedrive_d.tests.mocks import mock_logger
from tests.factory import account_factory, drive_factory

mock_logger.mock_loggers()


class TestDriveRoot(unittest.TestCase):
    def setUp(self):
        self.root = drive_factory.get_sample_drive_root()
        self.account = self.root.account

    def test_get_all_drives(self):
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                response_drives = [get_data('drive.json'), get_data('drive.json')]
                ids = [str(i) for i in range(0, 2)]
                for d in response_drives:
                    d['id'] = ids.pop(0)
                context.status_code = codes.ok
                return {'value': response_drives}

            mock.get(self.account.client.API_URI + '/drives', json=callback)
            all_drives = self.root.get_all_drives()
            all_ids = [str(i) for i in range(0, 2)]
            for i, x in all_drives.items():
                self.assertIn(i, all_ids)
                self.assertIsInstance(x, drives.DriveObject)
                all_ids.remove(i)
            self.assertEqual(0, len(all_ids))

    def run_get_drive(self, drive_id):
        """
        :param str | None drive_id:
        """
        with requests_mock.Mocker() as mock:
            path = '/drive'
            if drive_id is not None:
                path += 's/' + drive_id
            mock.get(self.account.client.API_URI + path, json=get_data('drive.json'))
            if drive_id is not None:
                drive = self.root.get_drive(drive_id)
            else:
                drive = self.root.get_default_drive()
            self.assertIsInstance(drive, drives.DriveObject)

    def test_get_drive(self):
        self.run_get_drive('123')

    def test_get_default_drive(self):
        self.run_get_drive(None)

    def test_add_cached_drive_errors(self):
        account = account_factory.get_sample_personal_account()
        drive_root = drives.DriveRoot(account)
        self.assertNotEqual('123', account.profile.user_id)
        self.assertRaises(ValueError, drive_root.add_cached_drive,
                          account_id='123', account_type=account.TYPE, drive=None)
        self.assertRaises(ValueError, drive_root.add_cached_drive,
                          account_id=account.profile.user_id, account_type='what', drive=None)

    def get_cached_drive_root_tuple(self):
        drive = drive_factory.get_sample_drive_object()
        drive_root = drive.root
        account = drive_root.account
        drive_root.add_cached_drive(account.profile.user_id, account.TYPE, drive)
        return drive_root, drive

    def test_get_drive_from_cache(self):
        drive_root, drive = self.get_cached_drive_root_tuple()
        self.assertIs(drive_root.get_drive(drive.drive_id, skip_cache=False), drive)

    @requests_mock.Mocker()
    def test_purge_cache(self, mock):
        data = get_data('drive_alt.json')
        drive_root, drive = self.get_cached_drive_root_tuple()
        mock.get(self.account.client.API_URI + '/drives/' + drive.drive_id, json=data)
        self.assertNotEqual(data['id'], drive.drive_id)
        self.assertIs(drive_root.get_drive(drive.drive_id, skip_cache=True), drive)
        self.assertEqual(data['id'], drive.drive_id)


if __name__ == '__main__':
    unittest.main()
