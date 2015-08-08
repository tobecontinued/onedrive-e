__author__ = 'xb'

import unittest

from onedrive_d.api import resources
from onedrive_d.tests import get_data


class TestItemReferenceResource(unittest.TestCase):
    data = get_data('item_reference_resource.json')

    def test_parse(self):
        ref = resources.ItemReferenceResource(self.data)
        self.assertEqual(self.data['driveId'], ref.drive_id)
        self.assertEqual(self.data['id'], ref.id)
        self.assertEqual(self.data['path'], ref.path)
        ref.id = 'AnotherValue'
        self.assertEqual('AnotherValue', ref.id)
        ref.path = '/foo/bar'
        self.assertEqual('/foo/bar', ref.path)


if __name__ == '__main__':
    unittest.main()
