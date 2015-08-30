__author__ = 'xb'

import unittest

from onedrive_d.common.task_worker import TaskConsumer
from onedrive_d.common import tasks
from onedrive_d.tests.common.test_tasks import BaseTestCase


class TestTaskConsumer(BaseTestCase, unittest.TestCase):
    def setUp(self):
        self.setup_objects()
        self.task = tasks.CreateDirTask(task_base=self.task_base, local_parent_path='', name='foo')
        self.task_pool.add_task(self.task)

    def test_exit(self):
        consumer = TaskConsumer(self.task_pool)
        consumer.start()
        TaskConsumer.terminate_sign.set()
        self.task_pool.semaphore.release()
        consumer.join(timeout=1)


if __name__ == '__main__':
    unittest.main()
