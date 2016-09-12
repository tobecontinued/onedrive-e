import os
import traceback

from onedrived import OS_USER_ID, OS_USER_GID
from onedrived.api import errors
from onedrived.common.dateparser import datetime_to_timestamp
from onedrived.common.tasks import TaskBase
from onedrived.store.items_db import ItemRecordStatuses


def get_tmp_filename(name):
    return '.' + name + '.!od'


class DownloadFileTask(TaskBase):
    def __init__(self, parent_task, rel_parent_path, item):
        """
        :param TaskBase parent_task: Base task.
        :param str rel_parent_path: Relative working path of this task.
        :param onedrived.api.items.OneDriveItem item: The item to download.
        """
        super().__init__(parent_task)
        self.rel_parent_path = rel_parent_path
        self._item = item
        self._item_name = item.name

    def handle(self):
        local_item_tmp_path = self.local_parent_path + get_tmp_filename(self.item_name)
        try:
            with open(local_item_tmp_path, 'wb') as f:
                self.drive.download_file(file=f, size=self._item.size, item_id=self._item.id)
            os.rename(local_item_tmp_path, self.local_path)
            t = datetime_to_timestamp(self._item.modified_time)
            os.utime(self.local_path, (t, t))
            os.chown(self.local_path, OS_USER_ID, OS_USER_GID)
            self.items_store.update_item(self._item, ItemRecordStatuses.DOWNLOADED)
        except (IOError, OSError) as e:
            self.logger.error('An IO error occurred when downloading "%s":\n%s.', self.local_path, traceback.format_exc())
        except errors.OneDriveError as e:
            self.logger.error('An API error occurred when downloading "%s":\n%s.', self.local_path, traceback.format_exc())
