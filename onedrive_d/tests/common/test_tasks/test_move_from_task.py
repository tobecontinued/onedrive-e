__author__ = 'xb'

import os
import unittest

try:
    from unittest import mock
except:
    import mock

from requests_mock import Mocker

from onedrive_d.common import tasks
from onedrive_d.tests.common import test_tasks


class TestMoveFromTask(test_tasks.BaseTestCase, unittest.TestCase):
    def setUp(self):
        super().setup_objects()
        self.task = tasks.MoveFromTask(self.task_base, '/foo/bar', 'baz', False)

    def test_is_solved(self):
        with Mocker():
            self.task.is_resolved = True
            self.task.handle()

    def test_item_restored(self):
        with Mocker():
            os.path.exists = lambda s: True
            self.task.handle()

    @mock.patch('onedrive_d.common.tasks.RemoveItemTask', handle=lambda o: None)
    def test_handle(self, mock_task):
        self.task.handle()
        self.assertTrue(mock_task.called)


if __name__ == '__main__':
    unittest.main()
