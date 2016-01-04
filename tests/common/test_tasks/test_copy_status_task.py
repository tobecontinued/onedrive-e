import os
import time
import unittest

import requests
from requests_mock import Mocker

from onedrived.api.errors import OneDriveError
from onedrived.api.resources import AsyncCopySession
from onedrived.common.tasks import copy_task, up_task
from tests import get_data, mock
from tests.common.test_tasks.test_copy_task import LOCATION_STR
from tests.factory.tasks_factory import get_sample_task_base


class TestCopyStatusTask(unittest.TestCase):
    def setUp(self):
        task_base = get_sample_task_base()
        task_base.rel_parent_path = '/'
        task_base.item_name = 'to.txt'
        self.data = get_data('image_item.json')
        self.async_status = AsyncCopySession(task_base.drive, {'Location': LOCATION_STR})
        self.task = copy_task.AsyncCopyMonitorTask(task_base, self.async_status)

    def build_mock(self, mock_req, url, status_code, data, headers=None):
        def callback(request, context):
            if headers:
                context.headers = headers
            context.status_code = status_code
            return data

        mock_req.get(url, json=callback)

    @Mocker()
    def test_handle_completed(self, mock_req):
        self.build_mock(mock_req, LOCATION_STR, requests.codes.see_other, {}, {'Location': 'http://bar'})
        self.build_mock(mock_req, 'http://bar', requests.codes.ok, self.data)
        self.task.handle()
        self.assertIsNone(self.task.task_pool.pop_task())
        self.assertEqual(1, len(self.task.items_store.get_items_by_id(item_id=self.data['id'])))

    @Mocker()
    def test_handle_in_progress(self, mock_req):
        self.assertIsNone(self.task.task_pool.pop_task())
        copy_task.AsyncCopyMonitorTask.POLLING_INTERVAL_SEC = 0.005
        self.build_mock(mock_req, LOCATION_STR, requests.codes.accepted, get_data('async_in_progress.json'))
        self.task.handle()
        time.sleep(0.02)
        self.assertIs(self.task, self.task.task_pool.pop_task())

    @Mocker()
    def test_handle_failed_fallback(self, mock_req):
        os.path.isfile = lambda p: True
        self.build_mock(mock_req, LOCATION_STR, requests.codes.accepted, get_data('async_failed.json'))
        self.task.handle()
        t = self.task.task_pool.pop_task()
        self.assertIsInstance(t, up_task.UploadFileTask)
        self.assertEqual(self.task.local_path, t.local_path)

    @Mocker()
    def test_handle_failed(self, mock_req):
        os.path.isfile = lambda p: False
        self.build_mock(mock_req, LOCATION_STR, requests.codes.accepted, get_data('async_failed.json'))
        self.task.handle()
        self.assertIsNone(self.task.task_pool.pop_task())

    def test_handle_error(self):
        self.async_status.update_status = mock.Mock(side_effect=OneDriveError(get_data('error_type1.json')))
        self.task.handle()


if __name__ == '__main__':
    unittest.main()
