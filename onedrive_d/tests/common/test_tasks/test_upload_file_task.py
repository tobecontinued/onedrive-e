__author__ = 'xb'

import io
import os
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


class TestUploadFileTask(test_tasks.BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setup_objects()
        self.task = tasks.UploadFileTask(self.task_base, local_parent_path='', name='test')
        self.file_path = self.drive.config.local_root + '/test'
        self.in_data = b'12345'
        os.path.getsize = lambda p: len(self.in_data)

    @Mocker()
    def test_handle(self, mock_request):
        output = io.BytesIO()
        data = get_data('image_item.json')

        def put_callback(request, context):
            output.write(request.body.getvalue())
            context.status_code = codes.created
            return data

        def patch_callback(request, context):
            j = request.json()
            self.assertEqual('1970-01-01T00:00:01Z', j['fileSystemInfo']['lastModifiedDateTime'])
            context.status_code = codes.ok
            return data

        mock_request.put(self.drive.get_item_uri(None, None) + '/test:/content', json=put_callback)
        mock_request.patch(self.drive.drive_uri + self.drive.drive_path + '/items/' + data['id'], json=patch_callback)
        os.path.getmtime = lambda p: 1
        m = mock.mock_open()
        m.return_value = io.BytesIO(self.in_data)
        with mock.patch('builtins.open', m, create=True):
            self.task.handle()
            import sys
            print(m.call_count, file=sys.stderr)
            print(m.method_calls, file=sys.stderr)
            print(m.call_args_list, file=sys.stderr)
        # m.assert_called_once_with(self.file_path, 'rb')
        self.assertEqual(self.in_data, output.getvalue())


if __name__ == '__main__':
    unittest.main()
