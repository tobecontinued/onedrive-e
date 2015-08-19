__author__ = 'xb'

import os

from onedrive_d.api import errors
from onedrive_d.api import options
from onedrive_d.common import logger_factory
from onedrive_d.store.items_db import ItemRecordStatuses


class TaskMixin:
    logger = logger_factory.get_logger('Tasks')

    @property
    def drive(self):
        return self._drive

    @drive.setter
    def drive(self, d):
        self._drive = d

    @property
    def items_store(self):
        return self._items_store

    @items_store.setter
    def items_store(self, s):
        self._items_store = s

    @property
    def task_pool(self):
        return self._task_pool

    @task_pool.setter
    def task_pool(self, p):
        self._task_pool = p


class NameReferenceMixin:
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n


class ItemReferenceMixin:
    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, n):
        self._item = n


class ParentPathReferenceMixin:
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


class LocalParentPathMixin(TaskMixin, ParentPathReferenceMixin):
    @property
    def local_parent_path(self):
        """
        :rtype: str
        """
        return self.parent_path.replace(self.drive.drive_path + '/root:', self.drive.config.local_root, 1)

    @local_parent_path.setter
    def local_parent_path(self, relative_path):
        """
        :param str relative_path:
        """
        self.parent_path = self.drive.drive_path + '/root:' + relative_path


class SynchronizeDirTask(TaskMixin):
    def __init__(self, task_base):
        pass

    def handle(self):
        pass


class CreateDirTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, local_parent_path, name, conflict_behavior=options.NameConflictBehavior.RENAME):
        self.task_base = task_base
        self.drive = task_base.drive
        self.items_store = task_base.items_store
        self.task_pool = task_base.task_pool
        self.local_parent_path = local_parent_path
        self.name = name
        self.conflict_behavior = conflict_behavior

    def handle(self):
        """
        Create a directory named self.name under self.parent_path or self.item_id.
        """
        try:
            new_item = self.drive.create_dir(name=self.name, parent_path=self.parent_path,
                                             conflict_behavior=self.conflict_behavior)
            self.parent_path = new_item.parent_reference.path
            if new_item.name != self.name:
                os.rename(self.local_parent_path + '/' + self.name, self.local_parent_path + '/' + new_item.name)
            self.items_store.update_item(new_item, ItemRecordStatuses.OK)
            self.logger.info('Created remote directory: %s/%s. Item ID: %s.', self.parent_path, new_item.name,
                             new_item.id)
            sync_task = SynchronizeDirTask(self.task_base)
            self.task_pool.add_task(sync_task)
        except errors.OneDriveError as e:
            self.logger.error("An API error occurred: %s.", e)


class RemoveItemTask(TaskMixin):
    def __init__(self, task_base):
        pass

    def handle(self):
        pass


class DownloadFileTask(ItemReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, item):
        self.drive = task_base.drive
        self.items_store = task_base.items_store
        self.task_pool = task_base.task_pool
        self.item = item
        self.parent_path = item.parent_reference.path

    def handle(self):
        local_item_path = self.local_parent_path + '/' + self.item.name
        try:
            with open(local_item_path, 'wb') as f:
                self.drive.download_file(file=f, size=self.item.size, item_id=self.item.id)
            self.items_store.update_item(self.item, ItemRecordStatuses.DOWNLOADED)
        except Exception as e:
            self.logger.error('Error occurred downloading to file "%s": %s.', local_item_path, e)


class UploadFileTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, local_parent_path, name, conflict_behavior=options.NameConflictBehavior.RENAME):
        self.task_base = task_base
        self.drive = task_base.drive
        self.items_store = task_base.items_store
        self.task_pool = task_base.task_pool
        self.local_parent_path = local_parent_path
        self.name = name
        self.conflict_behavior = conflict_behavior

    def handle(self):
        local_item_path = self.local_parent_path + '/' + self.name
        try:
            size = os.path.getsize(local_item_path)
            with open(local_item_path, 'rb') as f:
                item = self.drive.upload_file(
                    filename=self.name, data=f, size=size, parent_path=self.parent_path,
                    conflict_behavior=self.conflict_behavior)
                self.items_store.update_item(item, ItemRecordStatuses.UPLOADED)
        except Exception as e:
            self.logger.error('Error occurred when uploading "%s": %s.', local_item_path, e)


class MoveItemTask(TaskMixin):
    def __init__(self, task_base):
        pass

    def handle(self):
        pass


class CopyItemTask(TaskMixin):
    def __init__(self, task_base):
        pass

    def handle(self):
        pass


class UpdateItemInfoTask(TaskMixin):
    def __init__(self, task_base):
        pass

    def handle(self):
        pass
