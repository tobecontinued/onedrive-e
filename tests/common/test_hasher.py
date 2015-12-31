import io
import unittest

from onedrived.common import hasher
from tests import mock


class TestHasher(unittest.TestCase):
    def setUp(self):
        self.data = io.BytesIO(b'hello world!')

    def assert_func(self, func, args, expected_ret):
        m = mock.mock_open()
        m.return_value = self.data
        with mock.patch('builtins.open', m, create=True):
            ret = func('/foo/bar', **args)
            m.assert_called_once_with('/foo/bar', 'rb')
            self.assertEqual(expected_ret, ret, str(func))

    def test_crc32(self):
        self.assert_func(hasher.crc32_value, {}, '62177901')

    def test_sha1(self):
        self.assert_func(hasher.hash_value, {}, '430CE34D020724ED75A196DFC2AD67C77772D169')


if __name__ == '__main__':
    unittest.main()
