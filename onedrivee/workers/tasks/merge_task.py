import os
import traceback

from send2trash import send2trash

from onedrivee.common.utils import mkdir
from onedrivee.drives import errors
from onedrivee.common import hasher
from onedrivee.common.dateparser import datetime_to_timestamp, compare_timestamps
from onedrivee.workers.tasks.task_base import TaskBase
from onedrivee.workers.tasks.delete_task import DeleteItemTask
from onedrivee.workers.tasks.down_task import DownloadFileTask
from onedrivee.workers.tasks.up_task import UpdateMetadataTask
from onedrivee.workers.tasks.up_task import UploadFileTask
from onedrivee.workers.tasks.utils import append_hostname, stat_file
from onedrivee.workers.tasks.utils import unpack_first_item as _unpack_first_item
from onedrivee.store.items_db import ItemRecordStatuses



class MergeDirTask(TaskBase):
    def __init__(self, parent_task, rel_parent_path, item_name):
        super().__init__(parent_task)
        self.rel_parent_path = rel_parent_path
        self.item_name = item_name
        self.path_filter = self.drive.config.path_filter

    def handle(self):
        """
        Merge a remote directory with a local one.
        """
        if not os.path.isdir(self.local_path):
            self.logger.error('Failed to merge dir "%s". Path is not a directory.', self.local_path)
            return
        try:
            all_local_items = self._list_local_items()
            all_remote_items = self.drive.get_children(item_path=self.remote_path)
        except (IOError, OSError) as e:
            self.logger.error('Error occurred when synchronizing "%s":\n%s.', self.local_path, traceback.format_exc())
            return
        while all_remote_items.has_next:
            for remote_item in all_remote_items.get_next():
                all_local_items.discard(remote_item.name)  # Remove remote item from untouched list.
                if not self.path_filter.should_ignore(self.rel_path + '/' + remote_item.name, remote_item.is_folder) \
                        and not self.task_pool.has_pending_task(self.local_path + '/' + remote_item.name):
                    self._analyze_remote_item(remote_item, all_local_items)
        for local_item_name in all_local_items:
            self._analyze_local_item(local_item_name)

    def _list_local_items(self):
        """
        List all names under the task working directory.
        :return [str]: A list of entry names.
        """
        ent_list = set()
        ent_count = {}
        for ent in os.listdir(self.local_path):
            ent_path = self.local_path + '/' + ent
            is_dir = os.path.isdir(ent_path)
            filename, ext = os.path.splitext(ent)
            if self.path_filter.should_ignore(self.rel_path + '/' + ent, is_dir) or ext == '.!od':
                continue
            ent_lower = ent.lower()
            if ent_lower in ent_count:
                ent_count[ent_lower] += 1
                try:
                    ent = filename + ' ' + str(ent_count[ent_lower]) + ' (case conflict)' + ext
                    os.rename(ent_path, self.local_path + '/' + ent)
                    ent_count[ent.lower()] = 0
                except (IOError, OSError) as e:
                    self.logger.error('An error occurred when solving name conflict on "%s":\n%s.',
                                      self.local_path + '/' + ent, traceback.format_exc())
                    continue
            else:
                ent_count[ent_lower] = 0
            ent_list.add(ent)
        return ent_list

    def _analyze_remote_item(self, remote_item, all_local_items):
        """
        Analyze what to do with a remote item. Assume that this item passes ignore list.
        This function is the core algorithm. 
        :param onedrivee.api.items.OneDriveItem remote_item: The remote item object.
        :param [str] all_local_items: All remaining untouched local items.
        """
        item_local_path = self.local_path + '/' + remote_item.name
        q = self.items_store.get_items_by_id(parent_path=self.remote_path, item_name=remote_item.name)
        exists = os.path.exists(item_local_path)
        has_record = len(q) > 0
        if has_record:
          item_id, item_record = _unpack_first_item(q)
          has_record = item_id == remote_item.id
        if not has_record and not exists:
            # There is no record in database. The item is not present. Probably a new file.
            self._create_download_task(item_local_path, remote_item)
        elif has_record and not exists:
            # There is record but the file is gone.
            item_id, item_record = _unpack_first_item(q)
            if item_id == remote_item.id and remote_item.c_tag == item_record.c_tag \
                    and remote_item.e_tag == item_record.e_tag:
                # Same record. The file is probably deleted when daemon is off.
                self._create_delete_item_task(item_local_path, remote_item)
            else:
                # The record differs. For safety we download it.
                self.logger.info('Cannot determine actions for "%s". Non-existent and records differ.', item_local_path)
                self._create_download_task(item_local_path, remote_item)
        else:
            # The entry exists locally.
            # First solve possible type conflict.
            is_dir = os.path.isdir(item_local_path)
            if is_dir != remote_item.is_folder:
                self.logger.info('Type conflict on path "%s". One side is file and the other is dir.', item_local_path)
                self._move_existing_and_download(item_local_path, remote_item, all_local_items, q)
            elif is_dir:
                # Both sides are directories. Just update the record and sync if needed.
                if not has_record:
                    self.logger.info('Fix database record for directory "%s".', item_local_path)
                    self.items_store.update_item(remote_item, ItemRecordStatuses.OK, self.local_path)
                else:
                    self.logger.debug('Directory "%s" has intact record.', item_local_path)
                # add a MergeDirTask for the dir item
                self.logger.info('Add a MergeDirTask for directory "%s"', item_local_path)
                self._create_merge_dir_task(remote_item.name, remote_item)
            else:
                # Both sides are files. Examine file attributes.
                need_update = not has_record
                if has_record:
                    item_id, item_record = _unpack_first_item(q)
                    need_update = item_record.c_tag != remote_item.c_tag or item_record.e_tag != remote_item.e_tag
                if need_update:
                    self.logger.info('Fix database record for file "%s".',
                                     item_local_path)
                    self.items_store.update_item(remote_item, ItemRecordStatuses.OK, self.local_path)
                file_size, file_mtime = stat_file(item_local_path)
                if self._have_equal_hash(item_local_path, remote_item):
                    # Same file name. Same size. Same mtime. Guess they are the same for laziness.
                    self.logger.info('File "%s" seems fine.', item_local_path)
                else:
                    remote_item_modified_timestamp = datetime_to_timestamp(remote_item.modified_time)
                    if compare_timestamps(file_mtime, remote_item_modified_timestamp) > 0:
                        # The remote item did not change since last update, but LOCAL file changed since then.
                        self.logger.info('File "%s" changed locally since last sync. Upload.', item_local_path)
                        # TODO: it will update remote itme's modified time?
                        self._create_upload_task(local_item_name=remote_item.name, is_dir=False)
                    elif compare_timestamps(file_mtime, remote_item_modified_timestamp) <  0:
                        # The local item did not change since last update, but REMOTE file changed since then.
                        self.logger.info('File "%s" changed remotely since last sync. Download.', item_local_path)
                        self._create_download_task(item_local_path, remote_item)
                    else:
                        # Three ends mismatch. Keep both.
                        self.logger.info('Cannot determine file "%s". All information differ. Keep both.',
                                         item_local_path)
                        self._move_existing_and_download(item_local_path, remote_item, all_local_items, q)

    def _move_existing_and_download(self, item_local_path, remote_item, all_local_items, q):
        """
        Rename existing file and download the remote item there.
        :param str item_local_path:
        :param onedrivee.api.items.OneDriveItem remote_item:
        :param [str] all_local_items:
        :param dict[str, onedrivee.api.items.OneDriveItem] q:
        """
        try:
            resolved_name = append_hostname(item_local_path)
            all_local_items.add(resolved_name)
            if len(q) > 0:
                self.items_store.delete_item(parent_path=self.remote_path, item_name=remote_item.name)
            self._create_download_task(item_local_path, remote_item)
        except (IOError, OSError) as e:
            self.logger.error('IO error when renaming renaming "%s":\n%s.', item_local_path, traceback.format_exc())

    def _update_attr_when_hash_equal(self, item_local_path, item):
        t = datetime_to_timestamp(item.modified_time)
        try:
            self.logger.info('Updating timestamp for file "%s" to "%s".', item_local_path,
                             str(item.modified_time))
            os.utime(item_local_path, (t, t))
            self.items_store.update_item(item, ItemRecordStatuses.OK, self.local_path)
        except (IOError, OSError) as e:
            self.logger.error('IO error when updating timestamp for file "%s": %s', item_local_path, e)
            if not self.task_pool.has_pending_task(item_local_path):
                self.logger.info('Update server timestamp for file "%s" instead.', item_local_path)
                self.task_pool.add_task(UpdateMetadataTask(self, rel_parent_path=self.rel_path + '/',
                                                           item_name=item.name, new_mtime=t))

    def _create_delete_item_task(self, item_local_path, item):
        if not self.task_pool.has_pending_task(item_local_path):
            self.task_pool.add_task(DeleteItemTask(self, rel_parent_path=self.rel_path + '/', item_name=item.name,
                                                   is_folder=item.is_folder))

    def _create_download_task(self, item_local_path, item):
        """
        Create a new directory or download the file.
        :param str item_local_path:
        :param onedrivee.api.items.OneDriveItem item:
        """
        if item.is_folder:
            try:
                self.logger.info('Creating directory "%s".', item_local_path)
                mkdir(item_local_path)
                self.items_store.update_item(item, ItemRecordStatuses.OK, self.local_path)
                self._create_merge_dir_task(item.name, item)
            except (OSError, IOError) as e:
                self.logger.error('Error creating directory "%s":\n%s.', item_local_path, traceback.format_exc())
        else:
            if not self.task_pool.has_pending_task(item_local_path):
                self.logger.info('Will download file "%s".', item_local_path)
                self.task_pool.add_task(DownloadFileTask(self, rel_parent_path=self.rel_path + '/', item=item))

    def _analyze_local_item(self, local_item_name):
        """
        Analyze what to do with a local item that isn't found remotely. Assume that the item passes ignore list.
        :param str local_item_name: Name of the local item.
        """
        q = self.items_store.get_items_by_id(item_name=local_item_name, parent_path=self.remote_path)
        p = self.local_path + '/' + local_item_name
        is_dir = os.path.isdir(p)
        if len(q) > 0:
            # The item was on the server before, but now seems gone.
            item_id, item = _unpack_first_item(q)
            item_is_folder = item.crc32_hash == None
            if item_is_folder != is_dir:
                # The record is obsolete. Upload local entry.
                self.logger.info('The database record for %s is obsolete. Upload local entry "%s".', local_item_name, p)
                self.items_store.delete_item(item_name=local_item_name, parent_path=self.remote_path)
                self._create_upload_task(local_item_name, is_dir)
            else:
                # Type matched. Delete local entry.
                self.logger.info('The entry has been removed in remote. Delete the local one "%s".', p)
                self._send_path_to_trash(local_item_name, p)
        else:
            # The item has no record before. Probably new so upload it.
            # TODO: This can be made a little smarter by examining hash.
            self.logger.info('The item %s has no database record. Upload local entry "%s".', local_item_name, p)
            self._create_upload_task(local_item_name, is_dir)

    def _send_path_to_trash(self, local_item_name, local_path):
        try:
            send2trash(local_path)
            self.items_store.delete_item(item_name=local_item_name, parent_path=self.remote_path)
            self.logger.debug('Delete untouched local item "%s" as it seems deleted remotely.', local_path)
        except (IOError, OSError) as e:
            self.logger.error('An error occurred when deleting untouched local item "%s":\n%s.', local_path, traceback.format_exc())

    def _create_upload_task(self, local_item_name, is_dir):
        if is_dir:
            self._create_remote_dir(local_item_name)
        else:
            self.logger.debug('Created task uploading file "%s/%s".', self.rel_path, local_item_name)
            self.task_pool.add_task(UploadFileTask(self, self.rel_path + '/', local_item_name))

    def _create_merge_dir_task(self, name, item_obj):
        if not self.task_pool.has_pending_task(self.local_path + '/' + name):
            t = MergeDirTask(self, self.rel_path + '/', name)
            t.item_obj = item_obj
            self.task_pool.add_task(t)

    def _create_remote_dir(self, name):
        try:
            # FIXME: if self is root, self.item_obj is None:
            if self.item_obj is not None:
                new_item = self.drive.create_dir(name=name, parent_id=self.item_obj.id)
            else:
                new_item = self.drive.create_dir(name=name)
            self.items_store.update_item(new_item, ItemRecordStatuses.OK, self.local_path)
            self.logger.info('Created remote directory "%s".', self.local_path + '/' + name)
            self._create_merge_dir_task(name, new_item)
        except errors.OneDriveError as e:
            self.logger.error('An API error occurred creating remote dir "%s/%s":\n%s.', self.rel_path, name, traceback.format_exc())

    def _have_equal_hash(self, item_local_path, item):
        """
        :param str item_local_path:
        :param onedrivee.api.items.OneDriveItem item:
        :return True | False:
        """
        # TODO: use db to cache recent remote and local hash
        if item.file_props is not None and item.file_props.hashes is not None:
            # itme_sha may be None here.
            item_sha1 = item.file_props.hashes.sha1
            item_crc32 = item.file_props.hashes.crc32
        else:
            item_sha1 = None
            item_crc32 = None
        if item_sha1 is None:
            item_sha1 = self._computing_remote_hash_locally(item)
        local_sha1 = hasher.hash_value(item_local_path)

        self.logger.debug('File %s: remote: %s,%d, local: %s,%d', item_local_path, item_sha1, item.size, local_sha1,
            os.path.getsize(item_local_path))

        if item_crc32 is not None:
            self.logger.debug('Crc32 of file %s: remote:%s, local:%s', item_local_path, item_crc32,
                hasher.crc32_value(item_local_path))
        return  item_sha1 == local_sha1

    def _computing_remote_hash_locally(self, item):
        """
        we download it as a temp file and compute its hash
        then upload the hash value
        :param onedrivee.api.items.OneDriveItem item:
        :return remote file's hash value
        """
        local_item_tmp_path = self.local_parent_path + '.' + item.name + '.!od.hash'
        try:
            self.logger.debug('Compite hash value of remote file "%s" locally.', item.name)
            with open(local_item_tmp_path, 'wb') as f:
                self.drive.download_file(file=f, size=item.size, item_id=item.id)
                item_sha1 =  hasher.hash_value(local_item_tmp_path)
                os.remove(local_item_tmp_path)
                return item_sha1
        except (IOError, OSError) as e:
            self.logger.error('An IO error occurred when updating remote item hash "%s":\n%s.', local_item_tmp_path, traceback.format_exc())
        except errors.OneDriveError as e:
            self.logger.error('An API error occurred when updating remote item hash "%s":\n%s.', local_item_tmp_path, traceback.format_exc())
