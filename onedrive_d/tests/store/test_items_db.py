__author__ = 'xb'

import unittest

from onedrive_d.api import items
from onedrive_d.store import items_db
from onedrive_d.tests import get_data
from onedrive_d.tests.api import drive_factory
from onedrive_d.tests.mocks import mock_atexit

mock_atexit.mock_register()


class TestItemStorage(unittest.TestCase):
    record_keymap = {
        'item_id': 'id',
        'item_name': 'name',
        'type': 'type',
        'size': 'size',
        'etag': 'e_tag',
        'ctag': 'c_tag',
    }

    def setUp(self):
        self.all_items = []
        self.all_items_data = []
        self.drive = drive_factory.get_sample_drive_object()
        self.itemdb_mgr = items_db.ItemStorageManager(':memory:')
        self.itemdb = self.itemdb_mgr.get_item_storage(self.drive)
        for name in ['image_item.json', 'folder_item.json', 'folder_child_item.json']:
            self._add_item(name)

    def _add_item(self, filename):
        data = get_data(filename)
        item = items.OneDriveItem(self.drive, data)
        self.itemdb.update_item(item, items_db.ItemRecordStatuses.OK)
        self.all_items.append(item)
        self.all_items_data.append(data)

    def _process_kwargs(self, item, kwargs):
        if 'item_id' in kwargs:
            kwargs['item_id'] = item.id
        if 'item_name' in kwargs:
            kwargs['item_name'] = item.name
        if 'parent_path' in kwargs:
            kwargs['parent_path'] = item.parent_reference.path

    def assert_item_record(self, item, records, status=items_db.ItemRecordStatuses.OK):
        self.assertEqual(1, len(records))
        record = records[item.id]
        for kr, ki in self.record_keymap.items():
            self.assertEqual(getattr(item, ki), getattr(record, kr))
        item_parent = item.parent_reference
        self.assertEqual(item_parent.path, record.parent_path)
        self.assertEqual(item_parent.id, record.parent_id)
        self.assertEqual(item.created_time, record.created_time)
        self.assertEqual(item.modified_time, record.modified_time)
        if item.is_folder:
            self.assertIsNone(record.crc32_hash)
            self.assertIsNone(record.sha1_hash)
        else:
            file_props = item.file_props
            self.assertEqual(file_props.hashes.crc32, record.crc32_hash)
            self.assertEqual(file_props.hashes.sha1, record.sha1_hash)
        self.assertEqual(status, record.status)

    def run_get_item(self, index, **kwargs):
        item = self.all_items[index]
        self._process_kwargs(item, kwargs)
        records = self.itemdb.get_items_by_id(**kwargs)
        self.assert_item_record(item, records)

    def test_get_item_by_id(self):
        self.run_get_item(0, item_id='AUTO')

    def test_get_root_child_by_local_path(self):
        self.run_get_item(1, local_parent_path='', item_name='AUTO')

    def test_get_nested_child_by_local_path(self):
        self.run_get_item(2, local_parent_path='/Public', item_name='AUTO')

    def test_get_item_by_remote_path(self):
        self.run_get_item(1, parent_path='AUTO', item_name='AUTO')

    def run_delete_item(self, index, **kwargs):
        item = self.all_items[index]
        self._process_kwargs(item, kwargs)
        self.itemdb.delete_item(**kwargs)
        if 'is_folder' in kwargs:
            del kwargs['is_folder']
            records = self.itemdb._conn.execute('SELECT item_id FROM items').fetchall()
            self.assertEqual(1, len(records))
        else:
            records = self.itemdb.get_items_by_id(**kwargs)
            self.assertEqual(0, len(records))

    def test_delete_file_by_id(self):
        self.run_delete_item(0, item_id='AUTO')

    def test_delete_folder_by_id(self):
        self.run_delete_item(1, item_id='AUTO', is_folder=True)

    def test_delete_root_child_by_local_path(self):
        self.run_delete_item(1, local_parent_path='', item_name='AUTO', is_folder=True)

    def test_delete_nested_child_by_local_path(self):
        self.run_delete_item(2, local_parent_path='/Public', item_name='AUTO')

    def test_delete_item_by_remote_path(self):
        self.run_delete_item(1, parent_path='AUTO', item_name='AUTO', is_folder=True)

    def test_get_item_by_hash(self):
        item = self.all_items[0]
        records = self.itemdb.get_items_by_hash(crc32_hash=item.file_props.hashes.crc32)
        self.assert_item_record(item, records)

    def test_update_item(self):
        data = self.all_items_data[0]
        self.assertNotEqual('12345767', data['file']['hashes']['crc32Hash'])
        data['file']['hashes']['crc32Hash'] = '12345767'
        self.assertNotEqual('/drive/root:/foo', data['parentReference']['path'])
        data['parentReference']['path'] = '/drive/root:/foo'
        self.assertNotEqual('2020-01-20T03:04:05.06Z', data['lastModifiedDateTime'])
        data['lastModifiedDateTime'] = '2020-01-20T03:04:05.06Z'
        item = items.OneDriveItem(self.drive, data)
        status = items_db.ItemRecordStatuses.MOVING
        self.itemdb.update_item(item, status)
        records = self.itemdb.get_items_by_id(item_id=item.id)
        self.assert_item_record(item, records, status)

    def test_update_status(self):
        item = self.all_items[0]
        q = {'item_name': item.name, 'local_parent_path': ''}
        self.itemdb.update_status(items_db.ItemRecordStatuses.MOVING, **q)
        records = self.itemdb.get_items_by_id(**q)
        self.assert_item_record(item, records, items_db.ItemRecordStatuses.MOVING)

    def test_create_item_db_name(self):
        name = items_db.create_item_db_name(self.drive)
        self.assertIsInstance(name, str)

    def tearDown(self):
        self.itemdb.close()


if __name__ == '__main__':
    unittest.main()
