__author__ = 'xb'

import io
import unittest

try:
    from unittest import mock
except:
    import mock

from requests import codes
from requests_mock import Mocker

from onedrive_d.common import tasks
from onedrive_d.tests import get_data
from onedrive_d.tests.common import test_tasks
from onedrive_d.tests.mocks import mock_os


class TestUploadFileTask(test_tasks.BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setup_objects()
        self.task = tasks.UploadFileTask(self.task_base, local_parent_path='', name='test')
        self.file_path = self.drive.config.local_root + '/test'

    @Mocker()
    def test_handle(self, mock_request):
        in_data = b'12345'

        def callback(request, context):
            context.status_code = codes.created
            return get_data('image_item.json')

        mock_request.put(self.drive.get_item_uri(None, None) + '/test:/content', json=callback)
        mock_os.mock_getsize({self.file_path: len(in_data)})
        m = mock.mock_open(read_data=io.BytesIO(in_data))
        with mock.patch('__main__.open', m, create=True):
            self.task.handle()


if __name__ == '__main__':
    unittest.main()
