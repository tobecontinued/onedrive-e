import unittest

from onedrivee.api.errors import OneDriveError
from onedrivee.api.items import OneDriveItem
from onedrivee.common.tasks.delete_task import DeleteItemTask
from tests import get_data
from tests import mock
from tests.factory.tasks_factory import get_sample_task_base


class TestDeleteItemTask(unittest.TestCase):
    def setUp(self):
        data = get_data('folder_item.json')
        parent_task = get_sample_task_base()
        self.item = OneDriveItem(data=data, drive=parent_task.drive)
        self.task = DeleteItemTask(parent_task, rel_parent_path='/', item_name=self.item.name,
                                   is_folder=self.item.is_folder)
        self.task.items_store.update_item(self.item)

    def test_handle(self):
        m = mock.Mock(return_value=None)
        self.task.drive.delete_item = m
        self.task.handle()
        m.assert_called_once_with(item_path=self.item.parent_reference.path + '/' + self.item.name)
        self.assertEqual(0, len(self.task.items_store.get_items_by_id(item_id=self.item.id)))

    def test_handle_error(self):
        self.task.drive.delete_item = mock.Mock(side_effect=OneDriveError(get_data('error_token_expired.json')))
        self.task.handle()


if __name__ == '__main__':
    unittest.main()
