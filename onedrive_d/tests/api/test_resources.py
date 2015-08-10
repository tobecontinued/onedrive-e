__author__ = 'xb'

import unittest
from ciso8601 import parse_datetime

from onedrive_d.api import resources
from onedrive_d.tests import get_data


class TestItemReference(unittest.TestCase):
    data = get_data('item_reference.json')

    def test_parse(self):
        ref = resources.ItemReference(self.data)
        self.assertEqual(self.data['driveId'], ref.drive_id)
        self.assertEqual(self.data['id'], ref.id)
        self.assertEqual(self.data['path'], ref.path)

    def test_construct(self):
        ref = resources.ItemReference.build(id='AnotherValue', path='/foo/bar')
        self.assertEqual('AnotherValue', ref.id)
        self.assertEqual('/foo/bar', ref.path)


class TestUploadSession(unittest.TestCase):
    def test_parse(self):
        data = get_data('upload_session.json')
        session = resources.UploadSession(data)
        self.assertEqual(data['uploadUrl'], session.upload_url)
        self.assertEqual(parse_datetime(data['expirationDateTime']), session.expires_at)
        ranges = []
        for r in session.next_ranges:
            if r[1] is None:
                ranges.append(str(r[0]) + '-')
            else:
                ranges.append('%d-%d' % r)
        self.assertListEqual(data['nextExpectedRanges'], ranges)


if __name__ == '__main__':
    unittest.main()
