from onedrivee.common import logger_factory

__all__ = ['copy_task', 'delete_task', 'down_task', 'merge_task', 'move_task', 'up_task', 'utils']


class TaskBase:
    logger = logger_factory.get_logger('Tasks')

    def __init__(self, parent_task=None):
        """
        Initialize basic properties from the task from the parent task.
        :param TaskBase | None parent_task: The parent task. None for root task.
        """
        self._hold = False
        self._item = None
        if parent_task is not None:
            self.drive = parent_task.drive
            self.items_store = parent_task.items_store
            self.task_pool = parent_task.task_pool

    @property
    def drive(self):
        """
        :rtype: onedrivee.api.drives.DriveObject
        """
        return self._drive

    # noinspection PyAttributeOutsideInit
    @drive.setter
    def drive(self, d):
        self._drive = d

    @property
    def items_store(self):
        """
        :rtype: onedrivee.store.items_db.ItemStorage
        """
        return self._items_store

    # noinspection PyAttributeOutsideInit
    @items_store.setter
    def items_store(self, s):
        self._items_store = s

    @property
    def task_pool(self):
        """
        :rtype: onedrivee.store.task_pool.TaskPool
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
        """Relative parent path of the item referred to."""
        return self._rel_parent_path

    # noinspection PyAttributeOutsideInit
    @rel_parent_path.setter
    def rel_parent_path(self, v):
        """
        Set path relative to the repository root.
        :param str v: For root itself use ''; for item under root use '/' and always end with '/'.
        """
        self._rel_parent_path = v

    @property
    def remote_parent_path(self):
        p = self.drive.drive_path + '/root:' + self.rel_parent_path
        if p[-1] == '/':
            p = p[:-1]
        return p

    @property
    def local_parent_path(self):
        return self.drive.config.local_root + self.rel_parent_path

    @property
    def remote_path(self):
        if self.item_name == '':
        #root dir is '/drive/root:' without '/' in the tail
            return self.remote_parent_path        
        else:
            return self.remote_parent_path + '/' + self.item_name

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

    @property
    def should_hold(self):
        """
        :rtype: True | False
        """
        return self._hold

    @should_hold.setter
    def should_hold(self, v):
        """
        If set True, this task will hold the path it works on. It's then the task's responsibility to unhold the path.
        :param True | False v:
        """
        self._hold = v

    def handle(self):
        raise NotImplementedError('Subclass should override this stub.')
