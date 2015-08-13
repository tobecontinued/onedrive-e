__author__ = 'xb'

from ciso8601 import parse_datetime
import unittest

from onedrive_d.api import facets
from onedrive_d.api import items
from onedrive_d.api import resources
from onedrive_d.tests import get_data
from onedrive_d.tests import to_underscore_name
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


class TestOneDriveItem(unittest.TestCase):

    def setUp(self):
        self.data = get_data('image_item.json')
        self.data['audio'] = get_data('facets/audio_facet.json')
        self.data['deleted'] = get_data('facets/deleted_facet.json')
        self.data['photo'] = get_data('facets/photo_facet.json')
        self.data['video'] = get_data('facets/video_facet.json')
        self.data['specialFolder'] = get_data('facets/specialfolder_facet.json')
        self.data['location'] = get_data('facets/location_facet.json')
        self.data['parentReference'] = get_data('item_reference.json')
        self.item = items.OneDriveItem(drive=get_sample_drive_object(), data=self.data)

    def test_parse_props(self):
        fields = ['id', 'name', 'description', 'cTag', 'eTag', 'size', 'webUrl']
        for f in fields:
            self.assertEqual(self.data[f], getattr(self.item, to_underscore_name(f)), f)
        self.assertFalse(self.item.is_folder)
        self.assertEqual(items.OneDriveItemTypes.IMAGE, self.item.type)

    def assert_identity_facet(self, f, d):
        """
        :param onedrive_d.api.resources.IdentitySet f:
        :param dict[str, dict[str, str]] d: Source data dictionary.
        """
        self.assertIsInstance(f, resources.IdentitySet)
        for key in ['user', 'application', 'device']:
            if key not in d:
                self.assertIsNone(getattr(f, key), key + ' does not exist in data dictionary. Property should be None.')
            else:
                i = getattr(f, key)
                self.assertIsInstance(i, resources.Identity)
                self.assertEqual(d[key]['id'], i.id, key)
                self.assertEqual(d[key]['displayName'], i.display_name, key)

    def test_last_modified_by(self):
        self.assert_identity_facet(self.item.last_modified_by, self.data['lastModifiedBy'])

    def test_created_by(self):
        self.assert_identity_facet(self.item.created_by, self.data['createdBy'])

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

    def assert_prop(self, prop, type):
        facet = getattr(self.item, prop)
        self.assertIsInstance(facet, type, prop)

    def test_facets(self):
        all_facets = [
            ('audio_props', facets.AudioFacet),
            ('deleted_props', facets.DeletedFacet),
            ('photo_props', facets.PhotoFacet),
            ('special_folder_props', facets.SpecialFolderFacet),
            ('video_props', facets.VideoFacet),
            ('location_props', facets.LocationFacet),
            ('parent_reference', resources.ItemReference)
        ]
        for i in all_facets:
            prop, type = i
            self.assert_prop(prop, type)


class TestOneDriveItemTimestamps(unittest.TestCase):

    def setUp(self):
        self.data = get_data('image_item.json')
        self.assertNotIn('fileSystemInfo', self.data)

    def assert_timestamps(self, d, o):
        self.assertEqual(parse_datetime(d['createdDateTime']), o.created_time)
        self.assertEqual(parse_datetime(d['lastModifiedDateTime']), o.modified_time)

    def test_time_fallback(self):
        item = items.OneDriveItem(get_sample_drive_object(), self.data)
        self.assert_timestamps(self.data, item)

    def test_client_time(self):
        self.data['fileSystemInfo'] = get_data('facets/filesysteminfo_facet.json')
        self.assertNotEqual(self.data['fileSystemInfo']['createdDateTime'], self.data['createdDateTime'])
        self.assertNotEqual(self.data['fileSystemInfo']['lastModifiedDateTime'], self.data['lastModifiedDateTime'])
        item = items.OneDriveItem(get_sample_drive_object(), self.data)
        self.assert_timestamps(self.data['fileSystemInfo'], item)
        self.assert_timestamps(self.data['fileSystemInfo'], item.fs_info)

if __name__ == '__main__':
    unittest.main()
