import unittest

from onedrivee.api import facets
from onedrivee.api import resources
from onedrivee.common.dateparser import str_to_datetime
from tests import get_data
from tests import to_underscore_name


def assert_properties(test, data, obj):
    """
    Assuming data uses camelCase and obj properties uses underscored lowercase, test if the property in obj matches the
    value in data.
    :param unittest.TestCase test:
    :param dict[str, T] data:
    :param T obj:
    """
    for k, v in data.items():
        if 'DateTime' in k:
            k = k.replace('DateTime', 'Time')
            v = str_to_datetime(v)
        if 'lastModified' in k:
            k = k.replace('lastModified', 'modified')
        test.assertEqual(v, getattr(obj, to_underscore_name(k)), 'The property %s does not match data.' % k)


class TestFileSystemInfoFacet(unittest.TestCase):
    def setUp(self):
        self.data = get_data('facets/filesysteminfo_facet.json')
        self.facet = facets.FileSystemInfoFacet(self.data)

    def assert_timestamp(self, attr_name, dict_key, time_str):
        obj = facets.FileSystemInfoFacet(**{attr_name: str_to_datetime(time_str)})
        self.assertEqual(str_to_datetime(time_str), getattr(obj, attr_name, None))
        self.assertEqual(time_str, obj.data[dict_key])

    def test_parse(self):
        self.assertEqual(str_to_datetime(self.data['createdDateTime']), self.facet.created_time)
        self.assertEqual(str_to_datetime(self.data['lastModifiedDateTime']), self.facet.modified_time)

    def test_construct_ctime(self):
        self.assert_timestamp('created_time', 'createdDateTime', '2020-04-05T06:08:10Z')

    def test_construct_mtime(self):
        self.assert_timestamp('modified_time', 'lastModifiedDateTime', '2019-04-05T09:08:11Z')


class TestHashFacet(unittest.TestCase):
    def test_parse_malformed(self):
        h = facets.HashFacet({})
        self.assertIsNone(h.crc32)
        self.assertIsNone(h.sha1)


class TestFacets(unittest.TestCase):
    def assert_facet(self, filename, facet):
        data = get_data('facets/' + filename)
        obj = facet(data)
        assert_properties(self, data, obj)
        return obj

    def test_audio_facet(self):
        self.assert_facet('audio_facet.json', facets.AudioFacet)

    def test_deleted_facet(self):
        self.assert_facet('deleted_facet.json', facets.DeletedFacet)

    def test_location_facet(self):
        self.assert_facet('location_facet.json', facets.LocationFacet)

    def test_video_facet(self):
        self.assert_facet('video_facet.json', facets.VideoFacet)

    def test_quota_facet(self):
        self.assert_facet('quota_facet.json', facets.QuotaFacet)

    def test_photo_facet(self):
        self.assert_facet('photo_facet.json', facets.PhotoFacet)

    def test_special_folder_facet(self):
        self.assert_facet('specialfolder_facet.json', facets.SpecialFolderFacet)


class TestPermissionFacet(unittest.TestCase):
    """
    A combination test suie for PermissionFacet and SharingLinkFacet.
    """

    def setUp(self):
        self.data = get_data('facets/permission_facet.json')
        self.facet = facets.PermissionFacet(self.data)

    def test_permission_facet(self):
        self.assertEqual(self.data['id'], self.facet.id)
        self.assertListEqual(self.data['roles'], self.facet.roles)
        self.assertTrue(self.facet.can_read)
        self.assertTrue(self.facet.can_write)

    def test_sharing_link_facet(self):
        data = self.data['link']
        link = self.facet.link
        self.assertEqual(data['token'], link.token)
        self.assertEqual(data['type'], link.type)
        self.assertEqual(data['webUrl'], link.web_url)
        self.assertFalse(link.read_only)
        self.assertTrue(link.read_write)
        self.assertIsInstance(link.application, resources.Identity)
        assert_properties(self, data['application'], link.application)

    def test_inherited_from(self):
        inheritance = self.facet.inherited_from
        self.assertIsInstance(inheritance, resources.ItemReference)
        assert_properties(self, self.data['inheritedFrom'], inheritance)


if __name__ == '__main__':
    unittest.main()
