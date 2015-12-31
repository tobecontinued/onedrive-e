import time
import unittest

from onedrived.common.task_worker import TaskConsumer
from onedrived.common.tasks import TaskBase
from tests import mock
from tests.factory.db_factory import get_sample_task_pool
from tests.factory.drive_factory import get_sample_drive_object


class TestTaskConsumer(unittest.TestCase):
    def setUp(self):
        self.pool = get_sample_task_pool()
        self.worker = TaskConsumer(self.pool)
        self.task = TaskBase(None)
        self.task.drive = get_sample_drive_object()
        self.task.rel_parent_path = '/'
        self.task.item_name = 'foo'
        self.mock_handler = mock.Mock(return_value=None)
        self.task.handle = self.mock_handler

    def test_exec(self):
        # Start worker.
        self.worker.start()
        # Worker should respond to task addition.
        self.pool.add_task(self.task)
        time.sleep(0.01)
        self.mock_handler.assert_called_once_with()
        self.assertFalse(self.pool.has_pending_task(self.task.local_path))
        # Worker should gracefully exit.
        self.worker.terminate_sign.set()
        self.pool.semaphore.release()
        self.worker.join(timeout=1)


if __name__ == '__main__':
    unittest.main()
