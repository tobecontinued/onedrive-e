import threading

from onedrived.common import logger_factory


class TaskConsumer(threading.Thread):
    terminate_sign = threading.Event()
    logger = logger_factory.get_logger('TaskConsumer')

    def __init__(self, task_pool):
        """
        :param onedrived.store.task_pool.TaskPool task_pool:
        """
        super().__init__()
        self.daemon = True
        self.task_pool = task_pool

    def run(self):
        self.logger.debug('Started.')
        while True:
            self.task_pool.semaphore.acquire()
            if self.terminate_sign.is_set():
                break
            task = self.task_pool.pop_task()
            self.logger.debug('Acquired task of type "%s" on parent "%s", name "%s".',
                              type(task).__name__, task.local_parent_path, task.item_name)
            task.handle()
        self.logger.debug('Stopped.')


TaskConsumer.terminate_sign.clear()
