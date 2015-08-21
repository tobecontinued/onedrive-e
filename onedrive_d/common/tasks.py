__author__ = 'xb'

import os

from onedrive_d import mkdir
from onedrive_d import datetime_to_timestamp
from onedrive_d import timestamp_to_datetime
from onedrive_d.api import errors
from onedrive_d.api import facets
from onedrive_d.api import options
from onedrive_d.api import resources
from onedrive_d.common import logger_factory
from onedrive_d.store.items_db import ItemRecordStatuses


class TaskMixin:
    logger = logger_factory.get_logger('Tasks')

    def __init__(self, task_base=None, drive=None, items_store=None, task_pool=None):
        self.drive = drive if task_base is None else task_base.drive
        self.items_store = items_store if task_base is None else task_base.items_store
        self.task_pool = task_pool if task_base is None else task_base.task_pool

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

    @property
    def local_relative_parent_path(self):
        """
        :rtype: str
        """
        return self._local_relative_parent_path

    @local_parent_path.setter
    def local_parent_path(self, relative_path):
        """
        :param str relative_path: Path relative to drive's root directory.
        """
        self._local_relative_parent_path = relative_path
        self.parent_path = self.drive.drive_path + '/root:' + relative_path


class SynchronizeDirTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, local_parent_path, name):
        super().__init__(task_base)
        self.local_parent_path = local_parent_path
        self.name = name
        self.local_path = self.local_parent_path + '/' + name
        self.repo_relative_parent_path = '/' + self.local_relative_parent_path + '/' + self.name

    def list_items(self, path_filter):
        ent_list = {}
        ent_count = {}
        for ent in os.listdir(self.local_path):
            ent_path = self.local_path + '/' + ent
            is_folder = os.path.isfile(ent_path)
            if path_filter.should_ignore(self.repo_relative_parent_path + '/' + ent, is_folder):
                continue
            ent_lower = ent.lower()
            if ent_lower in ent_count:
                ent_count[ent_lower] += 1
                filename, ext = os.path.splitext(ent)
                try:
                    ent = filename + ' (case conflict ' + str(ent_count[ent_lower]) + ')' + ext
                    os.rename(ent_path, self.local_path + '/' + ent)
                    ent_count[ent.lower()] = 0
                except (IOError, OSError) as e:
                    self.logger.error('An error occurred when solving name conflict: %s.', e)
            else:
                ent_count[ent_lower] = 0
            ent_list[ent] = is_folder
        return ent_list

    def download_item(self, item, item_path):
        if item.is_folder:
            # If the item is a folder, create it and schedule a sync later.
            try:
                self.logger.debug('Creating directory "%s" as it does not exist locally and has no previous '
                                  'record.', item_path)
                mkdir(item_path)
                self.items_store.update_item(item)
                self.task_pool.add_task(SynchronizeDirTask(self, self.local_relative_parent_path + '/' +
                                                           self.name, item.name))
            except (IOError, OSError) as e:
                self.logger.error('Failed to create directory "%s": %s.', item_path, e)
        else:
            # Just download the item.
            self.logger.debug('Downloading "%s" as it does not exist locally and has no record in database.',
                              item_path)
            self.task_pool.add_task(DownloadFileTask(self, item))

    def analyze_item(self, item, all_local_items, path_filter):
        """
        :param onedrive_d.items.OneDriveItem item: A remote item.
        :param dict[str, True | False] all_local_items: All local items of interest.
        :param onedrive_d.common.path_filter.PathFilter path_filter: Path filter for the drive.
        """
        item_path = self.local_path + '/' + item.name
        try:
            is_exist = os.path.exists(item_path)
            del all_local_items[item.name]
        except Exception as e:
            self.logger.error('Cannot stat path "%s": %s', item_path, e)
            return
        q = self.items_store.get_items_by_id(item_id=item.id)
        if len(q) == 0 and not is_exist:
            # The item does not exist locally and we have no proof it was touched before.
            self.download_item(item, item_path)
        elif not is_exist:
            # Local record exists but the file was removed.
            pass
        elif len(q) == 0:
            # File exists but local record is missing
            pass
        else:
            # Local record exists and file exists
            pass

    def analyze_untouched_local_item(self, name):
        pass

    def handle(self):
        if not os.path.isdir(self.local_path):
            self.logger.error('Cannot sync path "%s" because it is not a directory.', self.local_path)
            return
        path_filter = self.drive.config.path_filter
        try:
            all_local_items = self.list_items(path_filter)
            all_remote_items = self.drive.get_children(item_path=self.parent_path + '/' + self.name)
        except (IOError, OSError) as e:
            self.logger.error('An error occurred synchronizing "%s": %s.', self.local_path, e)
            return
        while all_remote_items.has_next():
            remote_item_list = all_remote_items.get_next()
            for item in remote_item_list:
                if not path_filter.should_ignore(self.repo_relative_parent_path + '/' + item.name):
                    self.analyze_item(item, all_local_items, path_filter)
        for local_item_name in all_local_items:
            self.analyze_untouched_local_item(local_item_name)


class CreateDirTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, local_parent_path, name, conflict_behavior=options.NameConflictBehavior.RENAME):
        super().__init__(task_base=task_base)
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
            sync_task = SynchronizeDirTask(self, local_parent_path=self.local_relative_parent_path, name=self.name)
            self.task_pool.add_task(sync_task)
        except errors.OneDriveError as e:
            self.logger.error("An API error occurred: %s.", e)


class RemoveItemTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, local_parent_path, name, is_folder):
        super().__init__(task_base=task_base)
        self.local_parent_path = local_parent_path
        self.name = name
        self.is_folder = is_folder

    def handle(self):
        p = self.parent_path + '/' + self.name
        try:
            self.drive.delete_item(item_path=p)
            self.items_store.delete_item(parent_path=self.parent_path, item_name=self.name, is_folder=self.is_folder)
        except errors.OneDriveError as e:
            self.logger.error('An API error occurred when deleting "%s": %s.', p, e)


class DownloadFileTask(ItemReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, item):
        super().__init__(task_base=task_base)
        self.item = item
        self.parent_path = item.parent_reference.path

    def get_temp_filename(self):
        return '.' + self.item.name + '.!od_tmp'

    def handle(self):
        local_temp_path = self.local_parent_path + '/' + self.get_temp_filename()
        local_item_path = self.local_parent_path + '/' + self.item.name
        try:
            with open(local_temp_path, 'wb') as f:
                self.drive.download_file(file=f, size=self.item.size, item_id=self.item.id)
            os.rename(local_temp_path, local_item_path)
            t = datetime_to_timestamp(self.item.modified_time)
            os.utime(local_item_path, (t, t))
            self.items_store.update_item(self.item, ItemRecordStatuses.DOWNLOADED)
        except Exception as e:
            self.logger.error('Error occurred downloading to file "%s": %s.', local_item_path, e)


class UploadFileTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, local_parent_path, name, conflict_behavior=options.NameConflictBehavior.RENAME):
        super().__init__(task_base=task_base)
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
                modified_time = timestamp_to_datetime(os.path.getmtime(local_item_path))
                fs_info = facets.FileSystemInfoFacet(modified_time=modified_time)
                item = self.drive.update_item(item_id=item.id, new_file_system_info=fs_info)
                self.items_store.update_item(item, ItemRecordStatuses.OK)
        except Exception as e:
            self.logger.error('Error occurred when uploading "%s": %s.', local_item_path, e)


class MoveFromTask(NameReferenceMixin, LocalParentPathMixin):
    """
    A transient task that will become either RemoveItemTask or MoveItemTask.
    """

    def __init__(self, task_base, local_parent_path, name, is_folder=False):
        super().__init__(task_base=task_base)
        self.local_parent_path = local_parent_path
        self.name = name
        self.is_resolved = False
        self.is_folder = is_folder

    def handle(self):
        path = self.local_parent_path + '/' + self.name
        try:
            if self.is_resolved or os.path.exists(path):
                return
            RemoveItemTask(self, local_parent_path=self.local_relative_parent_path, name=self.name,
                           is_folder=self.is_folder).handle()
        except Exception as e:
            self.logger.error('An error occurred when touching "%s": %s.', path, e)


class MoveItemTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, move_from_task, local_parent_path, name):
        """
        :param onedrive_d.common.tasks.MoveFromTask move_from_task:
        :param str local_parent_path: New local relative parent path.
        :param str name: New name for the item.
        """
        super().__init__(move_from_task)
        move_from_task.is_resolved = True
        self.old_parent_path = move_from_task.parent_path
        self.old_name = move_from_task.name
        self.local_parent_path = local_parent_path
        self.name = name

    def handle(self):
        try:
            new_parent_reference = resources.ItemReference.build(path=self.parent_path)
            item = self.drive.update_item(item_path=self.old_parent_path + '/' + self.old_name, new_name=self.name,
                                          new_parent_reference=new_parent_reference)
            self.items_store.update_item(item, ItemRecordStatuses.OK)
        except errors.OneDriveError as e:
            self.logger.error('Error occurred when moving to "%s": %s.', self.local_parent_path + '/' + self.name, e)


class CopyItemTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, from_item_id, local_parent_path, new_name):
        super().__init__(task_base)
        self.from_item_id = from_item_id
        self.local_parent_path = local_parent_path
        self.name = new_name

    def handle(self):
        dest_reference = resources.ItemReference.build(path=self.local_parent_path)
        try:
            async_status = self.drive.copy_item(dest_reference=dest_reference, item_id=self.from_item_id,
                                                new_item_name=self.name)
            self.task_pool.add_task(CopyItemStatusMonitorTask(self, async_status, self.local_relative_parent_path,
                                                              self.name))
        except Exception as e:
            self.logger.error('Error occurred when moving to "%s": %s.', self.local_parent_path + '/' + self.name, e)


class CopyItemStatusMonitorTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, async_copy_status, local_parent_path, name):
        super().__init__(task_base)
        self.async_copy_status = async_copy_status
        self.local_parent_path = local_parent_path
        self.name = name

    def handle(self):
        path = self.local_parent_path + '/' + self.name
        try:
            self.async_copy_status.update_status()
            if self.async_copy_status.status == options.AsyncOperationStatuses.FAILED:
                # If failed, fall back to an upload task.
                if os.path.exists(path):
                    self.logger.info('Server failed to copy item "%s". Fall back to uploading.', path)
                    self.task_pool.add_task(UploadFileTask(self, local_parent_path=self.local_relative_parent_path,
                                                           name=self.name))
            elif self.async_copy_status.status == options.AsyncOperationStatuses.COMPLETED:
                # If completed, update the item.
                item = self.async_copy_status.get_completed_item()
                self.items_store.update_item(item, ItemRecordStatuses.OK)
            else:
                # Put the task back to task pool.
                self.task_pool.add_task(self)
        except errors.OneDriveError as e:
            self.logger.error('Error occurred when polling copy to "%s": %s.', path, e)


class UpdateItemInfoTask(NameReferenceMixin, LocalParentPathMixin):
    def __init__(self, task_base, local_parent_path, name, new_mtime):
        super().__init__(task_base)
        self.local_parent_path = local_parent_path
        self.name = name
        if isinstance(new_mtime, int):
            new_mtime = timestamp_to_datetime(new_mtime)
        self.new_mtime = new_mtime

    def handle(self):
        try:
            fs_info = facets.FileSystemInfoFacet(modified_time=self.new_mtime)
            new_item = self.drive.update_item(item_path=self.parent_path + '/' + self.name,
                                              new_file_system_info=fs_info)
            self.items_store.update_item(new_item, ItemRecordStatuses.OK)
        except errors.OneDriveError as e:
            self.logger.error('Error occurred when polling copy to "%s": %s.', self.local_parent_path + '/' +
                              self.name, e)
