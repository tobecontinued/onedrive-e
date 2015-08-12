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

    def test_build(self):
        ref = resources.ItemReference.build(id='AnotherValue', path='/foo/bar')
        self.assertEqual('AnotherValue', ref.id)
        self.assertEqual('/foo/bar', ref.path)

    def test_build_errors(self):
        self.assertRaises(ValueError, resources.ItemReference.build, id=None, path=None)

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


class TestIdentitySet(unittest.TestCase):
    data = {
        'user': {
            'id': 123,
            'displayName': 'John Doe'
        },
        'application': {
            'id': 444,
            'displayName': 'onedrive-d'
        },
        'device': {
            'id': 777,
            'displayName': 'Xubuntu'
        }
    }

    def test_full_identity(self):
        ident = resources.IdentitySet(self.data)

        self.assertIsInstance(ident.user, resources.Identity)
        self.assertEqual(ident.user.id, self.data['user']['id'])
        self.assertEqual(ident.user.display_name, self.data['user']['displayName'])

        self.assertIsInstance(ident.device, resources.Identity)
        self.assertEqual(ident.device.id, self.data['device']['id'])
        self.assertEqual(ident.device.display_name, self.data['device']['displayName'])

        self.assertIsInstance(ident.application, resources.Identity)
        self.assertEqual(ident.application.id, self.data['application']['id'])
        self.assertEqual(ident.application.display_name, self.data['application']['displayName'])

    def test_partial_identity(self):
        del self.data['user']
        ident = resources.IdentitySet(self.data)
        self.assertIsNone(ident.user)
        self.assertIsInstance(ident.device, resources.Identity)
        self.assertIsInstance(ident.application, resources.Identity)


if __name__ == '__main__':
    unittest.main()
