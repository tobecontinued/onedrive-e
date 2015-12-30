from time import sleep

from onedrive_d.api import errors
from onedrive_d.common.tasks import TaskBase


class DeleteItemTask(TaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name, is_folder, pause_sec=0):
        """
        :param TaskBase parent_task: Base task.
        :param str rel_parent_path: Relative working path of this task.
        :param str item_name: Name of the item to deal with.
        :param True | False is_folder: True to indicate the task is on a folder.
        :param int pause_sec: Time, in seconds, to wait before executing the task.
        """
        super().__init__(parent_task)
        self.rel_parent_path = rel_parent_path
        self.item_name = item_name
        self.is_folder = is_folder
        self.pause_sec = pause_sec
        self._handled = False
        self.handling = False

    @property
    def handled(self):
        return self._handled

    def set_handled(self):
        """
        MoveItemTask couldl set a delayed deletion task to "handled" status so that the latter can be skipped.
        """
        self._handled = True
        self.task_pool.mark_handled(self)
        self.logger.info('Delayed deletion task on "%s" has been handled externally.', self.local_path)

    def handle(self):
        self.handling = True
        if not self.handled and self.pause_sec > 0:
            try:
                sleep(self.pause_sec)
            except:
                pass
        if self.handled:
            return
        try:
            self.drive.delete_item(item_path=self.remote_path)
            if self.pause_sec > 0:
                self.task_pool.mark_handled(self)
            self.items_store.delete_item(parent_path=self.remote_parent_path, item_name=self.item_name,
                                         is_folder=self.is_folder)
            self.logger.info('Deleted entry "%s".', self.local_path)
            if self.is_folder:
                # Remove pending tasks of all its children
                self.task_pool.remove_children_tasks(self.local_path)
        except errors.OneDriveError as e:
            self.logger.error('An API error occurred when deleting "%s": %s.', self.local_path, e)
