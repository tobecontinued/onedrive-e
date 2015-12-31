import unittest

from onedrive_d.store import task_pool
from tests.factory.tasks_factory import get_sample_task_base


class TestTaskPool(unittest.TestCase):
    def setUp(self):
        self.task_base = get_sample_task_base()
        self.task_base.item_name = 'test'
        self.task_base.rel_parent_path = '/Public'
        self.task_pool = self.task_base.task_pool

    def test_get_instance(self):
        t1 = task_pool.TaskPool.get_instance()
        t2 = task_pool.TaskPool.get_instance()
        self.assertIsInstance(t1, task_pool.TaskPool)
        self.assertIs(t1, t2, 'Singleton getter should return same instance.')

    def test_add_pop_task(self):
        # Initially there is no task so pop returns None
        self.assertIsNone(self.task_pool.pop_task())
        self.task_pool.add_task(self.task_base)
        # Now add a task and there should be one pending on that path.
        self.assertTrue(self.task_pool.has_pending_task(self.task_base.local_path))
        # There is no task of type TestTaskPool
        self.assertIsNone(self.task_pool.pop_task(TestTaskPool))
        # But there is task
        self.assertIs(self.task_base, self.task_pool.pop_task(self.task_base.__class__))
        # The task has been popped.
        self.assertFalse(self.task_pool.has_pending_task(self.task_base.local_path))
        # Re-add it and do a pop without class specifier.
        self.task_pool.add_task(self.task_base)
        self.assertIs(self.task_base, self.task_pool.pop_task())

    def test_delete_children_task(self):
        self.task_pool.add_task(self.task_base)
        self.task_pool.remove_children_tasks(self.task_base.drive.config.local_root)
        self.assertFalse(self.task_pool.has_pending_task(self.task_base.local_path))


if __name__ == '__main__':
    unittest.main()
