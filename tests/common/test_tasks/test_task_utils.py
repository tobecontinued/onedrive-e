import os
import unittest

from onedrived import OS_HOSTNAME
from onedrived.common.tasks import utils
from tests import mock


class TestAppendHostnameUtil(unittest.TestCase):
    def setUp(self):
        os.rename = lambda f, t: None

    def test_append_hostname_no_number(self):
        os.path.exists = lambda p: False
        self.assertEqual('file (%s)' % OS_HOSTNAME, utils.append_hostname('file'))

    def test_append_hostname_number(self):
        with mock.patch('os.path.exists', side_effect=[True, True, False]):
            self.assertEqual('file 2 (%s)' % OS_HOSTNAME, utils.append_hostname('file'))


class TestStatFileUtil(unittest.TestCase):
    def test_stat_file(self):
        os.path.getsize = lambda p: 1
        os.path.getmtime = lambda p: 123123
        size, mtime = utils.stat_file('foobar')
        self.assertEqual(1, size)
        self.assertEqual(123123, mtime)


class TestMergeTaskHelperFunctions(unittest.TestCase):
    def test_unpack_first_item(self):
        d = {'key': 'val'}
        key, val = utils.unpack_first_item(d)
        self.assertEqual('key', key)
        self.assertEqual('val', val)
        self.assertEqual(1, len(d))


if __name__ == '__main__':
    unittest.main()
