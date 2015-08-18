__author__ = 'xb'

import unittest

from requests import codes
from requests_mock import Mocker

from onedrive_d.common import tasks
from onedrive_d.tests import get_data
from onedrive_d.tests.api import drive_factory
from onedrive_d.tests.mocks import mock_os
from onedrive_d.tests.store import db_factory


class BaseTestCase:
    # noinspection PyAttributeOutsideInit
    def setup_objects(self):
        self.rename_records = []
        self.drive = drive_factory.get_sample_drive_object()
        self.itemdb_mgr = db_factory.get_sample_item_storage_manager()
        self.items_db = self.itemdb_mgr.get_item_storage(self.drive)
        self.task_pool = db_factory.get_sample_task_pool()
        mock_os.mock_rename(self.rename_records)


class TestCreateDirTask(BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setup_objects()
        self.task = tasks.CreateDirTask(drive=self.drive, items_db=self.items_db, task_pool=self.task_pool)

    @Mocker()
    def test_something(self, mocker):
        self.task.item_name = 'foo'
        self.task.local_parent_path = ''

        def callback(request, context):
            self.assertEqual('foo', request.json()['name'])
            context.status_code = codes.created
            return get_data('new_dir_item.json')

        mocker.post(self.drive.get_item_uri(None, self.task.parent_path) + '/children', json=callback)
        self.task.handle()
        self.assertIn((self.drive.config.local_root + '/foo', self.drive.config.local_root + '/foo 2'),
                      self.rename_records)


if __name__ == '__main__':
    unittest.main()
