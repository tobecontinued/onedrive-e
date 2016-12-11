import os
import unittest

from onedrivee.api.errors import OneDriveError
from onedrivee.api.items import OneDriveItem
from onedrivee.common.tasks.up_task import CreateDirTask
from tests import get_data, mock
from tests.factory.tasks_factory import get_sample_task_base


class TestCreateDirTask(unittest.TestCase):
    def setUp(self):
        self.data = get_data('folder_item.json')
        parent_task = get_sample_task_base()
        self.task = CreateDirTask(parent_task, '/', self.data['name'])
        self.task.item_obj =  OneDriveItem(self.task.drive, self.data['parentReference'])
        self.mock_call = mock.Mock(return_value=OneDriveItem(drive=self.task.drive, data=self.data))
        self.task.drive.create_dir = self.mock_call
        self._backup_isdir = os.path.isdir

    def tearDown(self):
        os.path.isdir = self._backup_isdir

    def test_handle(self):
        os.path.isdir = lambda p: True
        self.task.handle()
        self.mock_call.assert_called_once_with(name=self.data['name'], parent_id=self.data['parentReference']['id'])
        self.assertEqual(1, len(self.task.items_store.get_items_by_id(item_id=self.data['id'])))

    def test_handle_OSError(self):
        os.path.isdir = mock.Mock(side_effect=OSError())
        self.task.handle()

    def test_handle_APIError(self):
        os.path.isdir = lambda p: True
        self.task.drive.create_dir = mock.Mock(side_effect=OneDriveError(get_data('error_type1.json')))
        self.task.handle()


if __name__ == '__main__':
    unittest.main()
