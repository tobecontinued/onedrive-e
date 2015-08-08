import unittest
import ciso8601

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
        self.assertEqual(ciso8601.parse_datetime(self.data['takenDateTime']), photo.taken_time)
        self.assertEqual(self.data['cameraMake'], photo.camera_make)
        self.assertEqual(self.data['cameraModel'], photo.camera_model)
        self.assertEqual(self.data['fNumber'], photo.f_number)
        self.assertEqual(self.data['exposureDenominator'], photo.exposure_denominator)
        self.assertEqual(self.data['exposureNumerator'], photo.exposure_numerator)
        self.assertEqual(self.data['focalLength'], photo.focal_length)
        self.assertEqual(self.data['iso'], photo.iso)


if __name__ == '__main__':
    unittest.main()
