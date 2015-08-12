__author__ = 'xb'

from ciso8601 import parse_datetime
import unittest

from onedrive_d.api import facets
from onedrive_d.api import items
from onedrive_d.api import resources
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
        self.assertIsInstance(last_modified_by, resources.IdentitySet)
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

    def test_image_facet(self):
        image_facet = self.item.image_props
        image_data = self.data['image']
        self.assertEqual(image_data['height'], image_facet.height)
        self.assertEqual(image_data['width'], image_facet.width)


class TestPhotoItem(unittest.TestCase):
    def setUp(self):
        self.data = get_data('image_item.json')
        self.data['photo'] = get_data('facets/photo_facet.json')
        self.data['location'] = get_data('facets/location_facet.json')
        self.data['parentReference'] = get_data('item_reference.json')
        del self.data['image']
        self.item = items.OneDriveItem(drive=get_sample_drive_object(), data=self.data)

    def test_photo_facet(self):
        facet = self.item.photo_props
        self.assertIsInstance(facet, facets.PhotoFacet)

    def test_location_facet(self):
        facet = self.item.location_props
        self.assertIsInstance(facet, facets.LocationFacet)

    def test_parent_reference(self):
        ref = self.item.parent_reference
        self.assertIsInstance(ref, resources.ItemReference)


if __name__ == '__main__':
    unittest.main()
