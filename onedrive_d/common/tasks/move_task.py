from onedrive_d.api import errors
from onedrive_d.api import resources
from onedrive_d.common.tasks import TaskBase
from onedrive_d.store.items_db import ItemRecordStatuses


class MoveItemTask(TaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name, move_from_task):
        """
        :param TaskBase parent_task:
        :param str rel_parent_path:
        :param str item_name:
        :param onedrive_d.common.tasks.delete_task.DeleteItemTask move_from_task: The deletion task on the old path.
        """
        super().__init__(parent_task)
        self.rel_parent_path = rel_parent_path
        self.item_name = item_name
        move_from_task.set_handled()  # Immediately mark the old task as handled externally.
        self.task_pool.delete_task(move_from_task)
        self._old_remote_item_path = move_from_task.remote_path

    def handle(self):
        try:
            new_parent_reference = resources.ItemReference.build(path=self.remote_parent_path)
            item = self.drive.update_item(item_path=self._old_remote_item_path, new_name=self.item_name,
                                          new_parent_reference=new_parent_reference)
            self.items_store.update_item(item, ItemRecordStatuses.OK)
        except errors.OneDriveError as e:
            self.logger.error('API error moving "%s" to "%s": %s.', self._old_remote_item_path, self.remote_path, e)
