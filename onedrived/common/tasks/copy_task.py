import os
import threading
from time import sleep

from onedrived.api import errors
from onedrived.api import options
from onedrived.api import resources
from onedrived.common.tasks import TaskBase
from onedrived.common.tasks.up_task import UploadFileTask
from onedrived.store.items_db import ItemRecordStatuses


class AsyncCopyItemTask(TaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name, from_item):
        """
        :param TaskBase parent_task:
        :param str rel_parent_path:
        :param str item_name:
        :param onedrived.api.items.OneDriveItem from_item:
        """
        super().__init__(parent_task)
        self.rel_parent_path = rel_parent_path
        self.item_name = item_name
        self._from_item = from_item

    def handle(self):
        try:
            new_parent_reference = resources.ItemReference.build(path=self.remote_parent_path)
            async_status = self.drive.copy_item(dest_reference=new_parent_reference, item_id=self._from_item.id,
                                                new_name=self.item_name)
            self.task_pool.add_task(AsyncCopyMonitorTask(self, async_status))
        except errors.OneDriveError as e:
            self.logger.error('API error copying item "%s" to "%s": %s.', self._from_item.id, self.remote_path, e)


class AsyncCopyMonitorTask(TaskBase):
    POLLING_INTERVAL_SEC = 60

    def __init__(self, parent_task, async_status):
        """
        :param AsyncCopyItemTask parent_task:
        :param onedrived.api.resources.AsyncCopySession async_status:
        """
        super().__init__(parent_task)
        self.rel_parent_path = parent_task.rel_parent_path
        self.item_name = parent_task.item_name
        self._async_status = async_status

    def put_back(self):
        self.logger.info('Copy for file "%s" is still in progress. Recheck in %d sec.',
                         self.local_path, self.POLLING_INTERVAL_SEC)
        sleep(self.POLLING_INTERVAL_SEC)
        self.task_pool.add_task(self)

    def handle(self):
        try:
            self._async_status.update_status()
            if self._async_status.status == options.AsyncOperationStatuses.FAILED:
                # If failed, fall back to an upload task.
                if os.path.isfile(self.local_path):
                    self.logger.info('Server failed to copy to item "%s". Upload the file instead.', self.remote_path)
                    self.task_pool.add_task(UploadFileTask(self, rel_parent_path=self.rel_parent_path,
                                                           item_name=self.item_name))
                else:
                    self.logger.error('Failed to copy file "%s" to server and local entry is no longer a file. Abort.',
                                      self.local_path)
            elif self._async_status.status == options.AsyncOperationStatuses.COMPLETED:
                # If completed, update the item.
                item = self._async_status.get_item()
                self.items_store.update_item(item, ItemRecordStatuses.OK)
                self.logger.info('Successfully copied file "%s" to server', self.local_path)
            else:
                # Put the task back to task pool.
                th = threading.Thread(target=self.put_back, args=())
                th.daemon = True
                th.start()
        except errors.OneDriveError as e:
            self.logger.error('API error when polling copy status for file "%s": %s.', self.local_path, e)
