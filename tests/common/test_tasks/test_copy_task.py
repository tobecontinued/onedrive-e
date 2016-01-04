import unittest

import requests
from requests_mock import Mocker

from onedrived.api.errors import OneDriveError
from onedrived.api.items import OneDriveItem
from onedrived.common.tasks import copy_task
from tests import get_data, mock
from tests.factory.tasks_factory import get_sample_task_base

LOCATION_STR = 'https://onedrive.com/monitor/113jlkjlkjasd1212abcascaf'


class TestCopyItemTask(unittest.TestCase):
    def setUp(self):
        task_base = get_sample_task_base()
        self.data = get_data('image_item.json')
        self.item = OneDriveItem(drive=task_base.drive, data=self.data)
        self.task = copy_task.AsyncCopyItemTask(task_base, '/', 'to.txt', self.item)

    @Mocker()
    def test_handle(self, mock_req):
        def callback(request, context):
            context.status_code = requests.codes.accepted
            context.headers = {'Location': LOCATION_STR}
            return ''

        mock_req.post(self.task.drive.drive_uri + '/drive/items/' + self.item.id + '/action.copy', body=callback)
        self.task.handle()
        self.assertTrue(self.task.task_pool.has_pending_task(self.task.local_path))

    def test_handle_error(self):
        self.task.drive.copy_item = mock.Mock(side_effect=OneDriveError(get_data('error_type1.json')))
        self.task.handle()


if __name__ == '__main__':
    unittest.main()
