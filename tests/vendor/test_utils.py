import unittest

from onedrivee.vendor import utils


class TestVendorUtils(unittest.TestCase):
    def test_print_bytes(self):
        self.assertEqual('1023.00 B', utils.pretty_print_bytes(1023, precision=2))

    def test_print_kb(self):
        self.assertEqual('1024.00 KB', utils.pretty_print_bytes(1024 << 10, precision=2))


if __name__ == '__main__':
    unittest.main()
