import os
import unittest

import onedrived


class TestGetCurrentOsUser(unittest.TestCase):
    def assert_values(self):
        user_id, user_name, user_home, user_gid = onedrived.get_current_os_user()
        self.assertIsInstance(user_id, int)
        self.assertIsInstance(user_name, str)
        self.assertIsInstance(user_home, str)
        self.assertIsInstance(user_gid, int)
        self.assertGreater(user_id, 0)  # must NOT be root
        self.assertGreater(len(user_home), 0)

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
