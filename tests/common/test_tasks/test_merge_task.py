import os
import unittest

from onedrivee.common.tasks.merge_task import MergeDirTask
from tests import mock
from tests.factory.tasks_factory import get_sample_task_base


class TestMergeTask(unittest.TestCase):
    def setUp(self):
        self.task = MergeDirTask(get_sample_task_base(), '', '')

    def test_list_local_items(self):
        """ list_local_items lists local items, renaming case-INsensitively duplicate ones and applying ignore list."""
        files = {
            'dir1.xxx': True,
            'Dir1.xxx': True,  # Case conflict with 'dir1'.
            'dir2': True,
            'file1': False,
            '.file1.!od': False
        }
        m = mock.Mock(return_value=None)
        os.listdir = lambda path: sorted(files.keys())
        os.path.isdir = lambda path: files[path.replace(self.task.local_path + '/', '', 1)]
        os.rename = m
        all_local_items = self.task._list_local_items()
        self.assertSetEqual({'Dir1.xxx', 'dir1 1 (case conflict).xxx', 'dir2', 'file1'}, all_local_items)
        m.assert_called_once_with(self.task.drive.config.local_root + '/' + 'dir1.xxx',
                                  self.task.drive.config.local_root + '/' + 'dir1 1 (case conflict).xxx')

    def test_list_local_items_error(self):
        """ If a file has naming conflict and fails, ignore it. """
        files = ['foo', 'Foo']
        os.listdir = lambda p: files
        os.path.isdir = lambda p: False
        m = mock.Mock(side_effect=OSError())
        os.rename = m
        all_local_items = self.task._list_local_items()
        self.assertSetEqual({'foo'}, all_local_items)


if __name__ == '__main__':
    unittest.main()
