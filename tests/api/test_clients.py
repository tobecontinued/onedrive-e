import unittest

from tests.factory import client_factory


class TestPersonalClient(unittest.TestCase):
    def test_get_auth_uri(self):
        client = client_factory.get_sample_personal_client()
        self.assertIsInstance(client.get_auth_uri(), str)


if __name__ == '__main__':
    unittest.main()
