__author__ = 'xb'

import threading

from onedrive_d.common import logger_factory
from onedrive_d.vendor import rwlock


class TaskPool:
    """
    An in-memory, singleton storage for Tasks based on hash maps.
    """

    logger = logger_factory.get_logger('TaskPool')
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._semaphore = threading.Semaphore()
            cls._lock = rwlock.RWLock()
            cls._instance = TaskPool()
        return cls._instance

    def __init__(self):
        self._all_tasks = []
        self._tasks_by_path = {}

    def _add_to_list(self, key, table, value):
        """
        Add an item to a dict whose values are lists.
        :param str key:
        :param dict[str, T] table:
        :param T value:
        """
        if key not in table:
            table[key] = [value]
        else:
            table[key].append(value)

    def get_task_path(self, task):
        """
        Return the local path the task performs on.
        :param onedrive_d.common.tasks.LocalParentPathMixin task:
        :return str:
        """
        return task.local_parent_path + '/' + task.name

    def add_task(self, task):
        self.logger.debug('Try acquiring writer lock...')
        self._lock.writer_acquire()
        self._all_tasks.append(task)
        self._add_to_list(self.get_task_path(task), self._tasks_by_path, task)
        self.logger.debug('Added task "%s" on path "%s".', task.__class__.__name__,
                          task.local_parent_path + '/' + task.name)
        self._lock.writer_release()
        self.logger.debug('Writer lock released.')
        self._semaphore.release()

    @property
    def semaphore(self):
        return self._semaphore

    def pop_task(self, task_class=None):
        self._lock.writer_acquire()
        ret = None
        if len(self._all_tasks) > 0:
            if task_class is None:
                ret = self._all_tasks.pop(0)
            else:
                for t in self._all_tasks:
                    if isinstance(t, task_class):
                        ret = t
                        self._all_tasks.remove(t)
                        break
        if ret is not None:
            self._tasks_by_path[self.get_task_path(ret)].remove(ret)
        self._lock.writer_release()
        return ret

    def has_pending_task(self, local_path):
        self._lock.reader_acquire()
        ret = local_path in self._tasks_by_path and len(self._tasks_by_path[local_path]) > 0
        self.logger.debug('Item "%s" has pending task? %s.', local_path, str(ret))
        self._lock.reader_release()
        return ret

    def remove_children_tasks(self, local_parent_path):
        local_parent_path += '/'
        self._lock.writer_acquire()
        for t in self._all_tasks:
            task_path = self.get_task_path(t)
            if task_path.startswith(local_parent_path):
                self._all_tasks.remove(t)
                self._tasks_by_path[task_path].remove(t)
        self._lock.writer_release()
