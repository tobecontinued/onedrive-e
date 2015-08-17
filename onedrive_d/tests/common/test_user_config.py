__author__ = 'xb'

import os
import unittest

from onedrive_d.common import user_config
from onedrive_d.common.drive_config import DriveConfig
from onedrive_d.tests import get_data
from onedrive_d.tests import assert_factory


class TestGetCurrentOsUser(unittest.TestCase):
    def assert_values(self):
        user_id, user_name, user_home = user_config.get_current_os_user()
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
    def setUp(self):
        self.data = {
            'http_retry_after_seconds': 40,
            'default_drive_config': DriveConfig(get_data('drive_config.json'))
        }
        self.user_conf = user_config.UserConfig(self.data)

    def test_parse(self):
        assert_factory.assert_dict_equals_attributes(self, self.data, self.user_conf)

    def test_dump(self):
        dump = self.user_conf.dump()
        load = self.user_conf.load(dump)
        self.assertIsInstance(load, user_config.UserConfig)
        self.assertEqual(self.user_conf.http_retry_after_seconds, load.http_retry_after_seconds)
        self.assertDictEqual(self.user_conf.default_drive_config.dump(), load.default_drive_config.dump())

    def test_take_effect(self):
        old_default = dict(DriveConfig.DEFAULT_VALUES)
        self.user_conf.take_effect()
        new_default = dict(DriveConfig.DEFAULT_VALUES)
        self.assertNotEqual(old_default, new_default)

    def test_append(self):
        del self.data['default_drive_config']
        conf = user_config.UserConfig(self.data)
        self.assertIsInstance(conf.default_drive_config, DriveConfig)


if __name__ == '__main__':
    unittest.main()
