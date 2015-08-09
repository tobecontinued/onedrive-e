__author__ = 'xb'

from ciso8601 import parse_datetime
import unittest

from onedrive_d.api import facets
from onedrive_d.api import identities
from onedrive_d.api import items
from onedrive_d.tests import get_data
from onedrive_d.tests.api.drive_factory import get_sample_drive_object


class TestRootItem(unittest.TestCase):

    def setUp(self):
        self.data = get_data('drive_root.json')
        self.item = items.OneDriveItem(drive=get_sample_drive_object(), data=self.data)

    def test_parse_folder(self):
        self.assertTrue(self.item.is_folder)
        self.assertEqual(self.data['folder']['childCount'], self.item.folder_props.child_count)

    def test_parse_modified_time(self):
        self.assertEqual(parse_datetime(self.data['fileSystemInfo']['lastModifiedDateTime']), self.item.modified_time)

    def test_children(self):
        for item_id, item_obj in self.item.children.items():
            self.assertEqual(item_id, item_obj.id)
            self.assertIsInstance(item_obj, items.OneDriveItem)


class TestImageItem(unittest.TestCase):
    data = get_data('image_item.json')

    def setUp(self):
        self.item = items.OneDriveItem(drive=get_sample_drive_object(), data=self.data)

    def test_parse_props(self):
        self.assertEqual(self.data['id'], self.item.id)
        self.assertEqual(self.data['name'], self.item.name)
        self.assertEqual((self.data['cTag']), self.item.c_tag)
        self.assertEqual((self.data['eTag']), self.item.e_tag)
        self.assertEqual((self.data['size']), self.item.size)
        self.assertFalse(self.item.is_folder)
        self.assertEqual(items.OneDriveItemTypes.IMAGE, self.item.type)

    def test_parse_created_time(self):
        self.assertEqual(parse_datetime(self.data['createdDateTime']), self.item.created_time)

    def test_parse_last_modified_facet(self):
        last_modified_by = self.item.last_modified_by
        self.assertIsInstance(last_modified_by, identities.IdentitySet)
        user = last_modified_by.user
        self.assertEqual(self.data['lastModifiedBy']['user']['displayName'], user.display_name)
        self.assertEqual(self.data['lastModifiedBy']['user']['id'], user.id)
        self.assertIsNone(last_modified_by.application)
        self.assertIsNone(last_modified_by.device)

    def test_parse_file_props_facet(self):
        file_facet = self.item.file_props
        self.assertIsInstance(file_facet, facets.FileFacet)
        self.assertEqual(self.data['file']['mimeType'], file_facet.mime_type)
        hashes = file_facet.hashes
        self.assertIsInstance(hashes, facets.HashFacet)
        self.assertDictEqual(
            self.data['file']['hashes'],
            {'crc32Hash': file_facet.hashes.crc32,
             'sha1Hash': file_facet.hashes.sha1})


if __name__ == '__main__':
    unittest.main()
