__author__ = 'xb'

import unittest

from onedrive_d.api import identities


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
        ident = identities.IdentitySet(self.data)

        self.assertIsInstance(ident.user, identities.Identity)
        self.assertEqual(ident.user.id, self.data['user']['id'])
        self.assertEqual(ident.user.display_name, self.data['user']['displayName'])

        self.assertIsInstance(ident.device, identities.Identity)
        self.assertEqual(ident.device.id, self.data['device']['id'])
        self.assertEqual(ident.device.display_name, self.data['device']['displayName'])

        self.assertIsInstance(ident.application, identities.Identity)
        self.assertEqual(ident.application.id, self.data['application']['id'])
        self.assertEqual(ident.application.display_name, self.data['application']['displayName'])

    def test_partial_identity(self):
        del self.data['user']
        ident = identities.IdentitySet(self.data)
        self.assertIsNone(ident.user)
        self.assertIsInstance(ident.device, identities.Identity)
        self.assertIsInstance(ident.application, identities.Identity)


if __name__ == '__main__':
    unittest.main()
