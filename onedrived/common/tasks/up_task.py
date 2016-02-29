import os

from onedrived.api import errors
from onedrived.api import facets
from onedrived.api.options import NameConflictBehavior
from onedrived.common.dateparser import timestamp_to_datetime
from onedrived.common.tasks import TaskBase
from onedrived.store.items_db import ItemRecordStatuses


class UpTaskBase(TaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name, conflict_behavior):
        super().__init__(parent_task)
        self.rel_parent_path = rel_parent_path
        self.item_name = item_name
        self._conflict_behavior = conflict_behavior

    def handle(self):
        raise NotImplementedError()


class CreateDirTask(UpTaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name, conflict_behavior=NameConflictBehavior.FAIL):
        super().__init__(parent_task, rel_parent_path, item_name, conflict_behavior)
        self.should_sync_parent = False

    def handle(self):
        try:
            if os.path.isdir(self.local_path):
                item = self.drive.create_dir(name=self.item_name, parent_path=self.remote_parent_path)
                self.items_store.update_item(item, ItemRecordStatuses.OK)
                self.logger.info('Created remote mapping for "%s".', self.local_path)
        except (IOError, OSError) as e:
            self.logger.error('IO error creating remote dir for "%s": %s.', self.local_path, e)
        except errors.OneDriveError as e:
            self.logger.error('API error creating remote dir for "%s": %s.', self.local_path, e)
            self.should_sync_parent = True


class UploadFileTask(UpTaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name, conflict_behavior=NameConflictBehavior.REPLACE):
        super().__init__(parent_task, rel_parent_path, item_name, conflict_behavior)
        self.should_hold = True

    def handle(self):
        try:
            size = os.path.getsize(self.local_path)
            with open(self.local_path, 'rb') as f:
                item = self.drive.upload_file(
                        filename=self.item_name, data=f, size=size, parent_path=self.remote_parent_path,
                        conflict_behavior=self._conflict_behavior)
                modified_time = timestamp_to_datetime(os.path.getmtime(self.local_path))
                fs_info = facets.FileSystemInfoFacet(modified_time=modified_time)
                item = self.drive.update_item(item_id=item.id, new_file_system_info=fs_info)
                self.items_store.update_item(item, ItemRecordStatuses.OK)
                self.logger.info('Uploaded file "%s".', self.local_path)
        except (IOError, OSError) as e:
            self.logger.error('IO error when uploading "%s": %s.', self.local_path, e)
        except errors.OneDriveError as e:
            self.logger.error('API error when uploading "%s": %s.', self.local_path, e)
        self.task_pool.clear_hold(self)


class UpdateMetadataTask(UpTaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name, new_mtime):
        super().__init__(parent_task, rel_parent_path, item_name, None)
        if isinstance(new_mtime, int):
            new_mtime = timestamp_to_datetime(new_mtime)
        self._new_mtime = new_mtime

    def handle(self):
        try:
            fs_info = facets.FileSystemInfoFacet(modified_time=self._new_mtime)
            new_item = self.drive.update_item(item_path=self.remote_path, new_file_system_info=fs_info)
            self.items_store.update_item(new_item, ItemRecordStatuses.OK)
        except errors.OneDriveError as e:
            self.logger.error('Error occurred updating server mtime for entry "%s": %s', self.local_path, e)
