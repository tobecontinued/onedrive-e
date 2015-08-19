import os
import unittest
import datetime

import onedrive_d


class TestTimeConversion(unittest.TestCase):
    s = '1970-01-01T00:01:01.123456Z'
    d = datetime.datetime(1970, 1, 1, 0, 1, 1, 123456)
    t = 61.1234560

    def test_convert(self):
        self.assertEqual(self.d, onedrive_d.str_to_datetime(self.s))
        self.assertEqual(self.s, onedrive_d.datetime_to_str(self.d))
        self.assertEqual(self.t, onedrive_d.datetime_to_timestamp(self.d))
        # self.assertEqual(self.s, onedrive_d.timestamp_to_str(self.t))


class TestGetCurrentOsUser(unittest.TestCase):
    def assert_values(self):
        user_id, user_name, user_home = onedrive_d.get_current_os_user()
        self.assertIsInstance(user_id, int)
        self.assertIsInstance(user_name, str)
        self.assertIsInstance(user_home, str)
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
