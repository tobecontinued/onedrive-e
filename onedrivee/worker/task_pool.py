import threading


class TaskPool:
    """
    An in-memory storage singleton for tasks.
    """

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = TaskPool()
        return cls._instance

    def __init__(self):
        self.tasks_by_path = {}
        self.queued_tasks = []
        self.semaphore = threading.Semaphore(0)
        self._lock = threading.Lock()

    def add_task(self, task):
        """
        Add a task to internal storage. It will not add if there is already a task on the path.
        :param onedrivee.common.tasks.TaskBase task: The task to add.
        """
        self._lock.acquire()
        if task.local_path in self.tasks_by_path:
            self._lock.release()
            return
        self.queued_tasks.append(task)
        self.tasks_by_path[task.local_path] = task
        self._lock.release()
        self.semaphore.release()

    def pop_task(self, task_class=None):
        """
        Pop the oldest task. It's required that the caller first acquire the semaphore.
        :param task_class: (Optional) Pop the first task of this given type.
        :return onedrivee.common.tasks.TaskBase | None: The first qualified task, or None.
        """
        self._lock.acquire()
        ret = None
        if len(self.queued_tasks) > 0:
            if task_class is None:
                ret = self.queued_tasks.pop(0)
            else:
                for t in self.queued_tasks:
                    if isinstance(t, task_class):
                        ret = t
                        self.queued_tasks.remove(t)
                        break
        if ret is not None and not ret.should_hold:
            del self.tasks_by_path[ret.local_path]
        self._lock.release()
        return ret

    def has_pending_task(self, local_path):
        with self._lock:
            return local_path in self.tasks_by_path

    def clear_hold(self, task):
        if task.local_path in self.tasks_by_path and self.tasks_by_path[task.local_path] is task:
            with self._lock:
                del self.tasks_by_path[task.local_path]

    def remove_children_tasks(self, local_parent_path):
        with self._lock:
            for t in self.queued_tasks[:]:
                if t.local_path.startswith(local_parent_path):
                    self.queued_tasks.remove(t)
                    del self.tasks_by_path[t.local_path]
