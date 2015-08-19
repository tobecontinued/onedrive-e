__author__ = 'xb'

import unittest

from requests import codes
from requests_mock import Mocker

from onedrive_d.api import items
from onedrive_d.common import tasks
from onedrive_d.tests import get_data
from onedrive_d.tests.common import test_tasks


class TestRemoveItemTask(test_tasks.BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setup_objects()
        self.all_items = []
        for filename in ['folder_item.json', 'folder_child_item.json']:
            item = items.OneDriveItem(self.drive, get_data(filename))
            self.all_items.append(item)
            self.items_store.update_item(item)
        self.task = tasks.RemoveItemTask(task_base=self.task_base, local_parent_path='', name='Public', is_folder=True)

    @Mocker()
    def test_handle(self, mock_request):
        mock_request.delete(self.drive.drive_uri + self.drive.drive_path + '/root:/Public', text='',
                            status_code=codes.no_content)
        self.task.handle()
        for item in self.all_items:
            q = self.items_store.get_items_by_id(item_id=item.id)
            self.assertEqual(0, len(q))


if __name__ == '__main__':
    unittest.main()
