import io
import os
import unittest

from onedrived.api.errors import OneDriveError
from onedrived.api.items import OneDriveItem
from onedrived.common.dateparser import timestamp_to_datetime
from onedrived.common.tasks.up_task import CreateDirTask
from onedrived.common.tasks.up_task import UpdateMetadataTask
from onedrived.common.tasks.up_task import UploadFileTask
from tests import get_data, mock
from tests.factory.tasks_factory import get_sample_task_base


class TestUpTaskBase(unittest.TestCase):
    def initialize_obj(self):
        self.data = get_data('image_item.json')
        self.parent_task = get_sample_task_base()
        self.item = OneDriveItem(drive=self.parent_task.drive, data=self.data)
        self.parent_task.drive.update_item = mock.Mock(return_value=self.item)


class TestCreateDirTask(unittest.TestCase):
    def setUp(self):
        self.data = get_data('folder_item.json')
        parent_task = get_sample_task_base()
        self.task = CreateDirTask(parent_task, '/', self.data['name'])
        self.mock_call = mock.Mock(return_value=OneDriveItem(drive=self.task.drive, data=self.data))
        self.task.drive.create_dir = self.mock_call

    def test_handle(self):
        os.path.isdir = lambda p: True
        self.task.handle()
        self.mock_call.assert_called_once_with(name=self.data['name'], parent_path=self.data['parentReference']['path'])
        self.assertEqual(1, len(self.task.items_store.get_items_by_id(item_id=self.data['id'])))

    def test_handle_OSError(self):
        os.path.isdir = mock.Mock(side_effect=OSError())
        self.task.handle()

    def test_handle_APIError(self):
        os.path.isdir = lambda p: True
        self.task.drive.create_dir = mock.Mock(side_effect=OneDriveError(get_data('error_type1.json')))
        self.task.handle()


class TestUploadFileTask(TestUpTaskBase):
    def setUp(self):
        self.initialize_obj()
        self.task = UploadFileTask(self.parent_task, '/', self.data['name'])
        self.parent_task.drive.upload_file = mock.MagicMock(return_value=self.item)

    def test_properties(self):
        self.assertEqual(self.data['name'], self.task.item_name)
        self.assertEqual(self.parent_task.drive.config.local_root + '/' + self.data['name'], self.task.local_path)

    def test_handle(self):
        os.path.getsize = lambda p: self.data['size']
        os.path.getmtime = lambda p: 123412341234
        m = mock.mock_open()
        m.return_value = io.BytesIO()
        with mock.patch('builtins.open', m, create=True):
            self.task.handle()
        self.assertEqual(1, len(self.task.items_store.get_items_by_id(item_id=self.item.id)))

    def test_handle_error(self):
        m = mock.mock_open()
        m.side_effect = OSError()
        with mock.patch('builtins.open', m, create=True):
            self.task.handle()


class TestUpdateMetadataTask(TestUpTaskBase):
    def setUp(self):
        self.initialize_obj()
        self.new_mtime = 123412341234
        self.task = UpdateMetadataTask(self.parent_task, '/', 'foo.txt', self.new_mtime)

    def test_handle(self):
        with mock.patch('onedrived.api.facets.FileSystemInfoFacet') as mock_class:
            self.task.handle()
            mock_class.assert_called_once_with(modified_time=timestamp_to_datetime(self.new_mtime))
        self.assertEqual(1, len(self.task.items_store.get_items_by_id(item_id=self.item.id)))

    def test_handle_error(self):
        self.parent_task.drive.update_item = mock.Mock(
            side_effect=OneDriveError(get_data('error_server_internal.json')))
        self.task.handle()


if __name__ == '__main__':
    unittest.main()
