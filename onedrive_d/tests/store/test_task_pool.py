__author__ = 'xb'

import unittest

from onedrive_d.common import tasks
from onedrive_d.store import task_pool
from onedrive_d.tests.common.test_tasks import BaseTestCase


class TestTaskPool(BaseTestCase, unittest.TestCase):
    def setUp(self):
        self.setup_objects()
        self.task = tasks.CreateDirTask(task_base=self.task_base, local_parent_path='', name='foo')
        self.task_pool.add_task(self.task)

    def test_add_and_pop(self):
        self.assertIs(self.task, self.task_pool.pop_task())

    def test_pop_by_class(self):
        self.assertIsNone(self.task_pool.pop_task(task_class=tasks.SynchronizeDirTask))
        self.assertIs(self.task, self.task_pool.pop_task(task_class=tasks.CreateDirTask))

    def test_has_pending_task(self):
        self.assertTrue(self.task_pool.has_pending_task(self.task_pool.get_task_path(self.task)))
        self.task_pool.pop_task()
        self.assertFalse(self.task_pool.has_pending_task(self.task_pool.get_task_path(self.task)))

    def test_singleton(self):
        a = task_pool.TaskPool.get_instance()
        b = task_pool.TaskPool.get_instance()
        self.assertIs(a, b)


if __name__ == '__main__':
    unittest.main()
