import unittest
from ciso8601 import parse_datetime

from onedrive_d.api import facets
from onedrive_d.tests import get_data


class TestQuotaFacet(unittest.TestCase):
    data = get_data('quota_facet.json')

    def test_parse(self):
        quota = facets.QuotaFacet(self.data)
        self.assertEqual(self.data['total'], quota.total)
        self.assertEqual(self.data['used'], quota.used)
        self.assertEqual(self.data['remaining'], quota.remaining)
        self.assertEqual(self.data['deleted'], quota.deleted)
        self.assertEqual(self.data['state'], quota.state)


class TestPhotoFacet(unittest.TestCase):
    data = get_data('photo_facet.json')

    def test_parse(self):
        photo = facets.PhotoFacet(self.data)
        self.assertEqual(parse_datetime(self.data['takenDateTime']), photo.taken_time)
        self.assertEqual(self.data['cameraMake'], photo.camera_make)
        self.assertEqual(self.data['cameraModel'], photo.camera_model)
        self.assertEqual(self.data['fNumber'], photo.f_number)
        self.assertEqual(self.data['exposureDenominator'], photo.exposure_denominator)
        self.assertEqual(self.data['exposureNumerator'], photo.exposure_numerator)
        self.assertEqual(self.data['focalLength'], photo.focal_length)
        self.assertEqual(self.data['iso'], photo.iso)


class TestFileSystemInfoFacet(unittest.TestCase):
    def setUp(self):
        self.data = {
            'createdDateTime': '2011-01-02T03:45:56Z',
            'lastModifiedDateTime': '2011-01-02T04:45:56Z'
        }
        self.facet = facets.FileSystemInfoFacet(self.data)

    def assert_timestamp(self, attr_name, time_str):
        obj = facets.FileSystemInfoFacet(**{attr_name: parse_datetime(time_str)})
        self.assertEqual(parse_datetime(time_str), getattr(obj, attr_name, None))

    def test_parse(self):
        self.assertEqual(parse_datetime(self.data['createdDateTime']), self.facet.created_time)
        self.assertEqual(parse_datetime(self.data['lastModifiedDateTime']), self.facet.modified_time)

    def test_construct_ctime(self):
        self.assert_timestamp('created_time', '2020-04-05T06:08:10Z')

    def test_construct_mtime(self):
        self.assert_timestamp('modified_time', '2019-04-05T09:08:11Z')


if __name__ == '__main__':
    unittest.main()
