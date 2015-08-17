__author__ = 'xb'

import os

from onedrive_d.api import errors
from onedrive_d.api import options
from onedrive_d.common import logger_factory
from onedrive_d.store.items_db import ItemRecordStatuses


class BaseTask:
    logger = logger_factory.get_logger('BaseTask')

    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        self.drive = drive
        self.task_pool = task_pool
        self.items_db = items_db
        self.item = None
        self.item_id = None
        self.item_name = None
        self.parent_path = None

    @property
    def item(self):
        """
        :rtype: onedrive_d.api.items.OneDriveItem
        """
        return self._item

    @item.setter
    def item(self, value):
        """
        :param onedrive_d.api.items.OneDriveItem | None value:
        """
        self._item = value
        if value is not None:
            self.item_id = value.id
            self.item_name = value.name
            self.parent_path = value.parent_reference.path

    @property
    def item_id(self):
        """
        :rtype str:
        """
        return self._item_id

    @item_id.setter
    def item_id(self, value):
        """
        :param str | None value:
        """
        self._item_id = value

    @property
    def parent_path(self):
        """
        :rtype: str
        """
        return self._parent_path

    @parent_path.setter
    def parent_path(self, path):
        """
        :param str | None path: Path relative to the OneDrive root.
        """
        self._parent_path = path

    @property
    def item_name(self):
        """
        :rtype: str
        """
        return self._item_name

    @item_name.setter
    def item_name(self, name):
        """
        :param str | None path: Path relative to the OneDrive root.
        """
        self._item_name = name

    @property
    def local_parent_path(self):
        """
        :rtype: str
        """
        return self.parent_path.replace(self.drive.drive_path + '/root:', self.drive.config.local_root, 1)

    @local_parent_path.setter
    def local_parent_path(self, local_path):
        """
        :param str local_path:
        """
        self.parent_path = self.drive.drive_path + '/root:' + local_path

    def handle(self):
        """
        Each task must implement its own way of handling the job.
        """
        raise NotImplementedError("Task %s did not implement handle()." % self.__class__.__name__)


class SynchronizeDirTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)

    def handle(self):
        pass


class CreateDirTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)
        self.conflict_behavior = options.NameConflictBehavior.RENAME

    @property
    def conflict_behavior(self):
        return self._conflict_behavior

    @conflict_behavior.setter
    def conflict_behavior(self, v):
        self._conflict_behavior = v

    def handle(self):
        """
        Create a directory named self.name under self.parent_path or self.item_id.
        """
        if self.item_name is None:
            raise ValueError('CreateDirTask got a task with directory name unset.')
        try:
            new_item = self.drive.create_dir(name=self.item_name, parent_id=self.item_id, parent_path=self.parent_path,
                                             conflict_behavior=self.conflict_behavior)
            self.parent_path = new_item.parent_reference.path
            if new_item.name != self.item_name:
                os.rename(self.local_parent_path + '/' + self.item_name, self.local_parent_path + '/' + new_item.name)
            self.items_db.update_item(new_item, ItemRecordStatuses.OK)
            self.logger.info('Created remote directory: %s/%s. Item ID: %s.', self.parent_path, new_item.name,
                             new_item.id)
            sync_task = SynchronizeDirTask(self.drive, self.items_db, self.task_pool)
            sync_task.item = new_item
            self.task_pool.add_task(sync_task)
        except errors.OneDriveError as e:
            self.logger.error("An API error occurred: %s.", e)


class RemoveItemTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)

    def handle(self):
        pass


class DownloadFileTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)

    def handle(self):
        pass


class UploadFileTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)

    def handle(self):
        pass


class MoveItemTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)

    def handle(self):
        pass


class CopyItemTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)

    def handle(self):
        pass


class UpdateItemInfoTask(BaseTask):
    def __init__(self, drive, items_db, task_pool):
        """
        :param onedrive_d.api.drives.DriveObject drive:
        :param onedrive_d.store.items_db.ItemStorage items_db:
        :param onedrive_d.store.task_pool.TaskPool task_pool:
        """
        super().__init__(drive, items_db, task_pool)

    def handle(self):
        pass
