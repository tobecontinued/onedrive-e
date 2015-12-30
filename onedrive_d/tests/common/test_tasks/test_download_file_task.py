import unittest

try:
    from unittest import mock
except:
    import mock

from requests import codes
from requests_mock import Mocker

from onedrive_d.api.items import OneDriveItem
from onedrive_d.common.tasks.down_task import get_tmp_filename, DownloadFileTask
from onedrive_d.tests import get_data
from onedrive_d.tests.common.test_tasks import get_sample_task_base, setup_os_mock


class TestDownloadFileTask(unittest.TestCase):

    def setUp(self):
        self.data = get_data('image_item.json')
        self.data['name'] = 'test'
        self.data['size'] = 1
        self.parent_task = get_sample_task_base()
        self.item = OneDriveItem(drive=self.parent_task.drive, data=self.data)
        self.task = DownloadFileTask(self.parent_task, rel_parent_path='/', item=self.item)
        self.calls_hist = setup_os_mock()

    @Mocker()
    def test_handle(self, mock_request):
        mock_request.get(self.task.drive.drive_uri + self.task.drive.drive_path + '/items/' + self.item.id + '/content',
                         content=b'1', status_code=codes.ok)

        m = mock.mock_open()
        with mock.patch('builtins.open', m, create=True):
            self.task.handle()
        self.assertEqual(1, len(self.calls_hist['os.rename']))
        self.assertEqual(1, len(self.calls_hist['os.chown']))
        self.assertEqual(1, len(self.calls_hist['os.utime']))
        m.assert_called_once_with(self.task.local_parent_path + get_tmp_filename('test'), 'wb')
        handle = m()
        handle.write.assert_called_once_with(b'1')


if __name__ == '__main__':
    unittest.main()
