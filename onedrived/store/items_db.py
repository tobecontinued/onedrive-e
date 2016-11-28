import atexit
import sqlite3
from urllib import parse as url_parse

from onedrived import get_content
from onedrived.common import logger_factory
from onedrived.common import hasher 
from onedrived.common.dateparser import datetime_to_str, str_to_datetime
from onedrived.vendor.rwlock import ReadWriteLock


def create_item_db_name(drive):
    account = drive.root.account
    return account.profile.user_id + '_' + account.TYPE + '_' + drive.drive_id + '.db'


class ItemRecordStatuses:
    OK = 'OK'
    DOWNLOADED = 'DOWNLOADED'
    MOVING = 'MOVING'
    UPLOADED = 'UPLOADED'


class ItemRecord:
    def __init__(self, row):
        self.item_id, self.type, self.item_name, self.parent_id, self.parent_path, self.e_tag, self.c_tag, self.size, \
        self.created_time, self.modified_time, self.status, self.crc32_hash, self.sha1_hash = row
        self.created_time = str_to_datetime(self.created_time)
        self.modified_time = str_to_datetime(self.modified_time)
        self.local_path = self.parent_path.split(':', 1)[1] + '/' + self.item_name


class ItemStorageManager:
    logger = logger_factory.get_logger('ItemStorageManager')
    def __init__(self, item_storage_dir):
        self.item_storage_dir = item_storage_dir
        self.item_storages = {}

    def get_item_storage(self, drive):
        """
        :param onedrived.api.drives.DriveObject drive:
        :return onedrived.store.items_db.ItemStorage: Item manager for the given drive.
        """
        if drive.drive_id not in self.item_storages:
            if self.item_storage_dir == ':memory:':
                db_path = ':memory:'
            else:
                db_path = self.item_storage_dir + '/' + create_item_db_name(drive)
            self.item_storages[drive.drive_id] = ItemStorage(db_path, drive)
        return self.item_storages[drive.drive_id]


class ItemStorage:
    """
    Local storage for items under ONE drive.
    """

    logger = logger_factory.get_logger('ItemStorage')
    create_table_sql_content = get_content('onedrive_items.sql')

    def __init__(self, db_path, drive):
        """
        :param str db_path: A unique path for the database to store items for the target drive.
        :param onedrived.api.drives.DriveObject drive: The underlying drive object.
        """
        if not hasattr(drive, 'storage_lock'):
            drive.storage_lock = ReadWriteLock()
        self.lock = drive.storage_lock
        self._conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
        self.drive = drive
        self._cursor = self._conn.cursor()
        self._cursor.execute(ItemStorage.create_table_sql_content)
        self._cursor.execute(get_content('onedrive_items.sql'))
        self._conn.commit()

    def __del__(self):
        self.close()

    def close(self):
        self._cursor.close()
        self._conn.close()

    def local_path_to_remote_path(self, path):
        return path.replace(self.drive.config.local_root, self.drive.drive_path + '/root:', 1)

    def remote_path_to_local_path(self, path):
        return path.replace(self.drive.drive_path + '/root:', self.drive.config.local_root,  1)

    def get_items_by_id(self, item_id=None, parent_path=None, item_name=None, local_parent_path=None):
        """
        FInd all qualified records from database by ID or path.
        :param str item_id: ID of the target item.
        :param str parent_path: Path reference of the target item's parent. Used with item_name.
        :param str item_name: Name of the item. Used with parent_path or local_parent_path.
        :param str local_parent_path: Local path to item's parent directory.
        :return dict[str, onedrived.store.items_db.ItemRecord]: All qualified records index by item ID.
        """
        if local_parent_path is not None:
            parent_path = self.local_path_to_remote_path(local_parent_path)
        args = {'item_id': item_id, 'parent_path': parent_path, 'item_name': item_name}
        return self.get_items(args)

    def get_items_by_hash(self, crc32_hash=None, sha1_hash=None):
        """
        Find all qualified records from database whose hash values match either parameter.
        :param str crc32_hash: CRC32 hash of the target item.
        :param str sha1_hash: SHA-1 hash of the target item.
        :return dict[str, onedrived.store.items_db.ItemRecord]: All qualified records index by item ID.
        """
        args = {'crc32_hash': crc32_hash, 'sha1_hash': sha1_hash}
        return self.get_items(args, 'OR')

    @staticmethod
    def _get_where_clause(args, relation='AND'):
        """
        Form a where clause in SQL query and the tuples for the filler values.
        :param dict[str, str | int]] args: Keys are where conditions and values are the filler values.
        :param str relation: Either 'AND' or 'OR'.
        :return (str, ()):
        """
        keys = []
        values = []
        for k, v in args.items():
            if v is not None:
                keys.append(k + '=?')
                values.append(v)
        relation = ' ' + relation + ' '
        return relation.join(keys), tuple(values)

    def get_items(self, args, relation='AND'):
        """
        :param dict[str, int | str] args: Criteria used to construct SQL query.
        :param str relation: Relation of the criteria.
        :return dict[str, onedrived.store.items_db.ItemRecord]: All matching rows in the form of ItemRecord.
        """
        where, values = self._get_where_clause(args, relation)
        ret = {}
        self.lock.acquire_read()
        q = self._conn.execute('SELECT item_id, type, item_name, parent_id, parent_path, etag, ctag, size, '
                               'created_time, modified_time, status, crc32_hash, sha1_hash FROM items WHERE ' +
                               where, values)
        for row in q.fetchall():
            item = ItemRecord(row)
            ret[item.item_id] = item
        self.lock.release_read()
        return ret

    def update_item(self, item, status=ItemRecordStatuses.OK, parent_path=None):
        """
        :param onedrived.api.items.OneDriveItem item:
        :param str status: One value of enum ItemRecordStatuses.
        :param str parent_path: If item does not have a parent reference, fallback to this path.
        """

        parent_ref = item.parent_reference
        try:
            # the remote url is encoding with ASCII, we should convert to unicode
            # note: item needs encoded url to download file content
            parent_path = url_parse.unquote(parent_ref.path)
        except Exception:
            pass

        if item.is_folder:
            crc32_hash = None
            sha1_hash = None
        else:
            file_facet = item.file_props
            #it seems some json response objects don't hava hash metadata
            if file_facet.hashes is not None:
                crc32_hash = file_facet.hashes.crc32
                sha1_hash = file_facet.hashes.sha1
            else:
                item_local_path = self.remote_path_to_local_path(parent_path + "/" + item.name)
                crc32_hash = hasher.crc32_value(item_local_path)
                sha1_hash = hasher.hash_value(item_local_path)
        
        created_time_str = datetime_to_str(item.created_time)
        modified_time_str = datetime_to_str(item.modified_time)
        self.lock.acquire_write()
        self._cursor.execute(
                'INSERT OR REPLACE INTO items (item_id, type, item_name, parent_id, parent_path, etag, '
                'ctag, size, created_time, modified_time, status, crc32_hash, sha1_hash)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (item.id, item.type, item.name, parent_ref.id, parent_path, item.e_tag, item.c_tag,
                 item.size, created_time_str, modified_time_str, status, crc32_hash, sha1_hash))
        self._conn.commit()
        self.lock.release_write()

    def delete_item(self, item_id=None, parent_path=None, item_name=None, local_parent_path=None, is_folder=False):
        """
        Delete the specified item from database. If the item is a directory, then also delete all its children items.
        :param str item_id: ID of the target item.
        :param str parent_path: Path reference of the target item's parent. Used with item_name.
        :param str item_name: Name of the item. Used with parent_path or local_parent_path.
        :param str local_parent_path: Local path to item's parent directory.
        :param True | False is_folder: True to indicate that the item is a folder (delete all children).
        """
        if local_parent_path is not None:
            parent_path = self.local_path_to_remote_path(local_parent_path)
        where, values = self._get_where_clause({'item_id': item_id, 'parent_path': parent_path, 'item_name': item_name})
        self.lock.acquire_write()
        if is_folder:
            # Translate ID reference to path and name reference.
            q = self._cursor.execute('SELECT item_id, parent_path, item_name FROM items WHERE ' + where, values)
            row = q.fetchone()
            if row is None:
                self.logger.warning('The folder to delete does not exist: %s, %s', where, str(values))
            else:
                item_id, parent_path, item_name = row
                self._cursor.execute('DELETE FROM items WHERE parent_id=? OR parent_path LIKE ?',
                                     (item_id, parent_path + '/' + item_name + '/%'))
        self._cursor.execute('DELETE FROM items WHERE ' + where, values)
        self._conn.commit()
        self.lock.release_write()

    def update_status(self, status, item_id=None, parent_path=None, item_name=None, local_parent_path=None):
        """
        Update the status tag of the target item.
        :param str status:
        :param str item_id: ID of the target item.
        :param str parent_path: Path reference of the target item's parent. Used with item_name.
        :param str item_name: Name of the item. Used with parent_path or local_parent_path.
        :param str local_parent_path: Path relative to drive's local root. If at root, use ''.
        """
        if local_parent_path is not None:
            parent_path = self.local_path_to_remote_path(local_parent_path)
        where, values = self._get_where_clause({'item_id': item_id, 'parent_path': parent_path, 'item_name': item_name})
        values = (status,) + values
        self.lock.acquire_write()
        self._cursor.execute('UPDATE items SET status=? WHERE ' + where, values)
        self._conn.commit()
        self.lock.release_write()
