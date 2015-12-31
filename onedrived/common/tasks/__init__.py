from onedrived.common import logger_factory

__all__ = ['copy_task', 'delete_task', 'down_task', 'merge_task', 'move_task', 'up_task', 'utils']


class TaskBase:
    logger = logger_factory.get_logger('Tasks')

    def __init__(self, parent_task=None):
        """
        Initialize basic properties from the task from the parent task.
        :param TaskBase parent_task: The parent task. None for root task.
        """
        if parent_task is not None:
            self.drive = parent_task.drive
            self.items_store = parent_task.items_store
            self.task_pool = parent_task.task_pool

    @property
    def drive(self):
        """
        :rtype: onedrived.api.drives.DriveObject
        """
        return self._drive

    # noinspection PyAttributeOutsideInit
    @drive.setter
    def drive(self, d):
        self._drive = d

    @property
    def items_store(self):
        """
        :rtype: onedrived.store.items_db.ItemStorage
        """
        return self._items_store

    # noinspection PyAttributeOutsideInit
    @items_store.setter
    def items_store(self, s):
        self._items_store = s

    @property
    def task_pool(self):
        """
        :rtype: onedrived.store.task_pool.TaskPool
        """
        return self._task_pool

    # noinspection PyAttributeOutsideInit
    @task_pool.setter
    def task_pool(self, p):
        self._task_pool = p

    @property
    def item_name(self):
        """
        :rtype: str
        """
        return self._item_name

    # noinspection PyAttributeOutsideInit
    @item_name.setter
    def item_name(self, n):
        self._item_name = n

    @property
    def rel_parent_path(self):
        """Relative parent path of the item referred to. Start with '/'."""
        return self._rel_parent_path

    # noinspection PyAttributeOutsideInit
    @rel_parent_path.setter
    def rel_parent_path(self, v):
        self._rel_parent_path = v

    @property
    def remote_parent_path(self):
        p = self.drive.drive_path + '/root:'
        if self.rel_parent_path != '/':
            p += self.rel_parent_path
        return p

    @property
    def local_parent_path(self):
        return self.drive.config.local_root + self.rel_parent_path

    @property
    def remote_path(self):
        return self.remote_parent_path + self.item_name

    @property
    def local_path(self):
        return self.local_parent_path + self.item_name

    @property
    def rel_path(self):
        return self.rel_parent_path + self.item_name

    @property
    def item_obj(self):
        return self._item

    # noinspection PyAttributeOutsideInit
    @item_obj.setter
    def item_obj(self, n):
        self._item = n

    def handle(self):
        raise NotImplementedError('Subclass should override this stub.')
