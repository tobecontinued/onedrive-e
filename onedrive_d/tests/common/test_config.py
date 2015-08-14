__author__ = 'xb'

import os
import unittest

from onedrive_d.common import config
from onedrive_d.tests import get_data


class TestGetCurrentOsUser(unittest.TestCase):
    def assert_values(self):
        user_id, user_name, user_home = config.get_current_os_user()
        self.assertIsInstance(user_id, int)
        self.assertIsInstance(user_name, str)
        self.assertIsInstance(user_home, str)
        self.assertGreater(user_id, 0)  # must NOT be root

    def test_types(self):
        """
        This test case only runs to see if an exception could happen.
        Does not verify correctness of returned values.
        """
        self.assert_values()

    def test_without_env(self):
        for k in ['USER', 'SUDO_USER']:
            if k in os.environ:
                del os.environ[k]
        self.assert_values()


class TestUserConfig(unittest.TestCase):
    data = get_data('user_config.json')
    conf = config.UserConfig(data)

    def test_parse(self):
        for k, v in self.data.items():
            self.assertEqual(v, getattr(self.conf, k))

    def test_append_default_values(self):
        del self.data['http_max_get_size_bytes']
        conf = config.UserConfig(self.data)
        self.assertEqual(config.UserConfig.http_max_get_size_bytes, conf.http_max_get_size_bytes)

    def test_serialize(self):
        dump = self.conf.data
        new_conf = config.UserConfig(dump)
        for k, v in self.conf.data.items():
            self.assertEqual(v, getattr(new_conf, k))


if __name__ == '__main__':
    unittest.main()
