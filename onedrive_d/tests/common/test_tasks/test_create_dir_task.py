__author__ = 'xb'

import unittest

from requests import codes
from requests_mock import Mocker

from onedrive_d.tests.common import test_tasks
from onedrive_d.common import tasks
from onedrive_d.tests import get_data


class TestCreateDirTask(test_tasks.BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setup_objects()
        self.task = tasks.CreateDirTask(task_base=self.task_base, local_parent_path='', name='foo')

    @Mocker()
    def test_handle(self, mocker):
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
