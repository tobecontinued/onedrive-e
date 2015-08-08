__author__ = 'xb'

import ciso8601
import unittest

from onedrive_d.api import facets
from onedrive_d.api import identities
from onedrive_d.api import items
from onedrive_d.tests import get_data


class TestImageItem(unittest.TestCase):
    data = get_data('image_item.json')

    def setUp(self):
        self.item = items.OneDriveItem(data=self.data)

    def test_parse_props(self):
        self.assertEqual(self.data['id'], self.item.id)
        self.assertEqual(self.data['name'], self.item.name)
        self.assertEqual((self.data['cTag']), self.item.c_tag)
        self.assertEqual((self.data['eTag']), self.item.e_tag)
        self.assertEqual((self.data['size']), self.item.size)
        self.assertFalse(self.item.is_folder)
        self.assertEqual(items.OneDriveItemTypes.IMAGE, self.item.type)

    def test_parse_created_time(self):
        self.assertEqual(ciso8601.parse_datetime(self.data['createdDateTime']), self.item.created_time)

    def test_parse_last_modified_facet(self):
        last_modified_by = self.item.last_modified_by
        self.assertIsInstance(last_modified_by, identities.IdentitySet)
        self.assertEqual(self.data['lastModifiedBy']['user']['displayName'], last_modified_by.user.display_name)
        self.assertEqual(self.data['lastModifiedBy']['user']['id'], last_modified_by.user.id)
        self.assertIsNone(last_modified_by.application)
        self.assertIsNone(last_modified_by.device)

    def test_parse_file_props_facet(self):
        file_facet = self.item.file_props
        self.assertIsInstance(file_facet, facets.FileFacet)
        self.assertEqual(self.data['file']['mimeType'], file_facet.mime_type)
        hashes = file_facet.hashes
        self.assertIsInstance(hashes, facets.HashFacet)
        self.assertEqual(self.data['file']['hashes']['crc32Hash'], file_facet.hashes.crc32)
        self.assertEqual(self.data['file']['hashes']['sha1Hash'], file_facet.hashes.sha1)


if __name__ == '__main__':
    unittest.main()
