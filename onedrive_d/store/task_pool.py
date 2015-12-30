import threading


class TaskPool:
    """
    An in-memory storage singleton for tasks.
    """

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TaskPool()
        return cls._instance

    def __init__(self):
        self.tasks_by_path = {}
        self.queued_tasks = []
        self.unhandled_tasks = []
        self.semaphore = threading.Semaphore(0)
        self._lock = threading.Lock()

    def add_task(self, task):
        """
        Add a task to internal storage.
        :param onedrive_d.common.tasks.TaskBase task: The task to add.
        """
        self._lock.acquire()
        self.queued_tasks.append(task)
        if task.local_path not in self.tasks_by_path:
            self.tasks_by_path[task.local_path] = [task]
        else:
            self.tasks_by_path[task.local_path].append(task)
        self._lock.release()
        self.semaphore.release()

    def pop_task(self, task_class=None):
        """
        Pop the oldest task. It's required that the caller first acquire the semaphore.
        :param task_class: (Optional) Pop the first task of this given type.
        :return onedrive_d.common.tasks.TaskBase | None: The first qualified task, or None.
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
        if ret is not None:
            self.tasks_by_path[ret.local_path].remove(ret)
            # Handle delayed tasks.
            if hasattr(ret, 'handled') and hasattr(ret, 'pause_sec') and ret.pause_sec > 0:
                self.unhandled_tasks.append(ret)
        self._lock.release()
        return ret

    def get_task_by_local_path(self, local_path, task_class=None):
        self._lock.acquire()
        if local_path in self.tasks_by_path:
            if task_class is None:
                ret = self.tasks_by_path[local_path].copy()
            else:
                ret = [t for t in self.tasks_by_path[local_path] if isinstance(t, task_class)]
        else:
            ret = []
        if len(self.unhandled_tasks) > 0:
            if task_class is None:
                ret += [t for t in self.unhandled_tasks if t.local_path == local_path]
            else:
                ret += [t for t in self.unhandled_tasks if isinstance(t, task_class) and t.local_path == local_path]
        self._lock.release()
        return ret

    def delete_task(self, task):
        self._lock.acquire()
        if task.local_path in self.tasks_by_path and task in self.tasks_by_path[task.local_path]:
            self.tasks_by_path[task.local_path].remove(task)
        if task in self.unhandled_tasks:
            self.unhandled_tasks.remove(task)
        if task in self.queued_tasks:
            self.queued_tasks.remove(task)
        self._lock.release()

    def has_pending_task(self, local_path):
        # FIXME: this function should have been atomic with any subsequent add / pop call.
        self._lock.acquire()
        ret = local_path in self.tasks_by_path and len(self.tasks_by_path[local_path]) > 0
        self._lock.release()
        return ret

    def mark_handled(self, task):
        self._lock.acquire()
        if task in self.unhandled_tasks:
            self.unhandled_tasks.remove(task)
        self._lock.release()

    def remove_children_tasks(self, local_parent_path):
        to_be_deleted = []
        self._lock.acquire()
        for t in self.queued_tasks:
            if t.local_path.startswith(local_parent_path):
                to_be_deleted.append(t)
                self.tasks_by_path[t.local_path].remove(t)
        self.queued_tasks -= to_be_deleted
        self.unhandled_tasks -= to_be_deleted
        self._lock.release()
