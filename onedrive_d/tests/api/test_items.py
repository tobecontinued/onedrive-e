__author__ = 'xb'

import ciso8601
import unittest

from onedrive_d.api import facets
from onedrive_d.api import identities
from onedrive_d.api import items
from onedrive_d.tests import get_data


class TestImageItem(unittest.TestCase):
    data = get_data('image_item.json')

    def test_parse(self):
        item = items.OneDriveItem(data=self.data)
        self.assertEqual(self.data['id'], item.id)
        self.assertEqual(self.data['name'], item.name)
        self.assertEqual(ciso8601.parse_datetime(self.data['createdDateTime']), item.created_time)
        self.assertFalse(item.is_folder)
        self.assertEqual(items.OneDriveItemTypes.IMAGE, item.type)
        self.assertEqual((self.data['cTag']), item.c_tag)
        self.assertEqual((self.data['eTag']), item.e_tag)
        self.assertEqual((self.data['size']), item.size)
        last_modified_by = item.last_modified_by
        self.assertIsInstance(last_modified_by, identities.IdentitySet)
        self.assertEqual(self.data['lastModifiedBy']['user']['displayName'], last_modified_by.user.display_name)
        self.assertEqual(self.data['lastModifiedBy']['user']['id'], last_modified_by.user.id)
        self.assertIsNone(last_modified_by.application)
        self.assertIsNone(last_modified_by.device)
        file_facet = item.file_props
        self.assertIsInstance(file_facet, facets.FileFacet)
        self.assertEqual(self.data['file']['mimeType'], file_facet.mime_type)
        hashes = file_facet.hashes
        self.assertIsInstance(hashes, facets.HashFacet)
        self.assertEqual(self.data['file']['hashes']['crc32Hash'], file_facet.hashes.crc32)
        self.assertEqual(self.data['file']['hashes']['sha1Hash'], file_facet.hashes.sha1)


if __name__ == '__main__':
    unittest.main()
