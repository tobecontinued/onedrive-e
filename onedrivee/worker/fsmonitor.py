import csv
import os
import shutil
import subprocess
import threading

from onedrivee.common.logger_factory import get_logger
from onedrivee.common.tasks import TaskBase
from onedrivee.common.tasks import delete_task, merge_task, move_task, up_task, utils


def _get_rel_parent_path(drive, local_parent_path):
    """
    Translate a local path to path relative to drive local root. E.g., '/home/xb/OneDrive/foo.bar' -> '/foo.bar'.
    :param onedrivee.api.drives.DriveObject drive:
    :param str local_parent_path:
    :return str: Path relative to drive local root.
    """
    return local_parent_path.replace(drive.config.local_root, '', 1)


# TODO: there are still some issues to let a task occupy a path until it's completed.
# TODO: finish the class.

class FileSystemMonitor(threading.Thread):
    MOVE_DETECTION_DELAY_SEC = 4
    SYNC_PARENT_DELAY_SEC = 60

    logger = get_logger('fsmon')

    def __init__(self, drive_store, items_store_manager, task_pool):
        """
        :param onedrivee.store.drives_db.DriveStorage drive_store:
        :param onedrivee.store.items_db.ItemStorageManager items_store_manager:
        :param onedrivee.store.task_pool.TaskPool task_pool:
        """
        super().__init__(name='fsmon', daemon=True)
        self._items_store_man = items_store_manager
        self._task_pool = task_pool
        self._all_drives = drive_store.get_all_drives().values()
        self._running = False
        self._delayed_tasks = set()
        self._task_bases = dict()
        self._preprocess_drives()

    def _enqueue_delayed_task(self, task):
        """
        :param onedrivee.common.tasks.TaskBase task:
        """
        if task in self._delayed_tasks:
            self._task_pool.add_task(task)

    def _find_drive(self, path):
        for d in self._all_drives:
            if path.startswith(d.config.local_root):
                return d

    def _preprocess_drives(self):
        for drive in self._all_drives:
            task_base = TaskBase(None)
            task_base.drive = drive
            task_base.task_pool = self._task_pool
            task_base.items_store = self._items_store_man.get_item_storage(drive)
            self._task_bases[drive] = task_base

    def _sync_parent_dir_of(self, drive, rel_path):
        rel_parent_path, dir_name = rel_path.rsplit('/', maxsplit=1)
        task = merge_task.MergeDirTask(self._task_bases[drive], rel_parent_path=rel_parent_path, item_name=dir_name)
        self._task_pool.add_task(task)

    def _process_create_dir_event(self, drive, local_parent_path, dir_name):
        """
        Subroutine to handle the event that a new directory is created.
        :param onedrivee.api.drives.DriveObject drive:
        :param str local_parent_path: Local path to the parent of this newly created directory.
        :param str dir_name: Name of the newly created directory.
        """
        rel_parent_path = _get_rel_parent_path(drive, local_parent_path)
        task = up_task.CreateDirTask(self._task_bases[drive], rel_parent_path=rel_parent_path, item_name=dir_name)
        task.handle()
        if task.should_sync_parent:
            self._sync_parent_dir_of(drive, rel_parent_path)

    def _process_delete_event(self, drive, local_parent_path, ent_name, is_folder):
        """
        Subroutine to handle the event that an entry is deleted.
        :param onedrivee.api.drives.DriveObject drive:
        :param str local_parent_path:
        :param str ent_name:
        :param True | False is_folder: True to indicate that the deleted item is a directory.
        """
        rel_parent_path = _get_rel_parent_path(drive, local_parent_path)
        task = delete_task.DeleteItemTask(parent_task=self._task_bases[drive], rel_parent_path=rel_parent_path,
                                          item_name=ent_name, is_folder=is_folder)
        self._task_pool.add_task(task)

    def _process_move_from_event(self, drive, local_parent_path, ent_name, is_folder):
        # First try finding the item in database.
        rel_parent_path = _get_rel_parent_path(drive, local_parent_path)
        item_store = self._items_store_man.get_item_storage(drive)
        q = item_store.get_items_by_id(local_parent_path=local_parent_path, item_name=ent_name)
        try:
            item_id, item = q.popitem()
            if item.is_folder != is_folder:
                raise KeyError()
        except KeyError:
            # If the record does not match, sync the parent after some time.
            threading.Timer(self.SYNC_PARENT_DELAY_SEC, self._sync_parent_dir_of, (drive, rel_parent_path))
            return
        task = delete_task.DeleteItemTask(parent_task=self._task_bases[drive], rel_parent_path=rel_parent_path,
                                          item_name=ent_name, is_folder=is_folder)
        task.item_obj = item
        self._delayed_tasks.add(task)
        threading.Timer(self.MOVE_DETECTION_DELAY_SEC, self._enqueue_delayed_task, task)

    def _convert_delete_dir_to_move(self, drive, local_parent_path, ent_name):

        for t in self._delayed_tasks:
            if isinstance(t, delete_task.DeleteItemTask)

    def _process_move_to_event(self, drive, local_parent_path, ent_name):
        local_path = local_parent_path + '/' + ent_name
        item_store = self._items_store_man.get_item_storage(drive)
        try:
            is_folder = os.path.isdir(local_path)
            for t in self._delayed_tasks:
                pass
                # if not isinstance(t, delete_task.DeleteItemTask) or t.local_parent_path != local_parent_path \
                #        or t.item_name !:
                #    pass
                #    continue
                # if t.item_obj.is_folder == is_folder:

    def _process_event(self, event_str, local_parent_path, ent_name):
        """
        The event dispatcher.
        :param str event_str:
        :param str local_parent_path:
        :param str ent_name:
        """
        drive = self._find_drive(local_parent_path)
        if event_str == 'CREATE,ISDIR':
            # A new directory was created. The directory might have name conflict with existing item, and might have
            # been deleted by the time CreateDirTask runs. It might have been added new files to as well. Therefore,
            # handle this type of event synchronously.
            # If there is no network, this handle will be blocked. But if no network, tasks will pile up anyway.
            self._process_create_dir_event(drive, local_parent_path, ent_name)
        elif 'CLOSE_WRITE' in event_str:
            # A file that opened in writable mode was closed. If the file is being uploaded, the current upload session
            # should be aborted. Also the task to upload that file could have been fetched by a worker and not traceable
            # in TaskPool.
            pass
        elif 'MOVED_FROM' in event_str:
            # Add delayed move to a queue. Use a new thread to add it to the task queue later.
            # A better way is to use asyncio, but it is not part of Python 3.3 standard (which adds extra dependency).
            self._process_move_from_event(drive, local_parent_path, ent_name, 'ISDIR' in event_str)
        elif 'MOVED_TO' in event_str:
            self._process_move_to_event(drive, local_parent_path, ent_name)
        elif 'DELETE' in event_str:
            self._process_delete_event(drive, local_parent_path, ent_name, 'ISDIR' in event_str)

    def close(self):
        """ An external thread should call close() and then join() this thread (to finish the last task) to stop. """
        if self._running:
            subprocess.call(['kill', '-s', '9', str(self._subp.pid)])
            self._running = False

    def run(self):
        if not shutil.which('inotifywait'):
            self.logger.critical('Cannot start file system monitor because command "inotifywait" was not found.')
            return
        self._running = True
        self.logger.info('Starting.')
        args = ['inotifywait', '--quiet', '--csv', '-e', 'unmount,create,close_write,delete,move',
                '--exclude', '\..*\.!od', '-mr'] + [drive.config.local_root for drive in self._all_drives]
        self._subp = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        reader = csv.reader(self._subp.stdout)
        for row in reader:
            local_parent_path, event_str, ent_name = row
            self._process_event(event_str, local_parent_path, ent_name)
        self.logger.info('Stopped.')
