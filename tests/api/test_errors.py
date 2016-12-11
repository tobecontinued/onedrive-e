import unittest

from onedrivee.api import errors
from tests import get_data


class TestOneDriveError(unittest.TestCase):
    def test_parse_type1(self):
        data = get_data('error_type1.json')
        error = errors.OneDriveError(data)
        self.assertEqual(data['error']['code'], error.errno)
        self.assertEqual(data['error']['message'], error.strerror)

    def test_parse_type2(self):
        data = get_data('error_type2.json')
        error = errors.OneDriveError(data)
        self.assertEqual(data['error'], error.errno)
        self.assertEqual(data['error_description'], error.strerror)

    def test_invaild_format(self):
        self.assertRaises(errors.OneDriveInvaildRepsonseFormat, errors.OneDriveError, {})


class TestOneDriveTokenErrorConversion(unittest.TestCase):
    def raise_error(self, filename, expected_error):
        data = get_data(filename)
        self.assertIsInstance(errors.OneDriveError(data), expected_error)

    def test_parse_token_expired_error(self):
        self.raise_error('error_token_expired.json', errors.OneDriveTokenExpiredError)

    def test_parse_server_internal_error(self):
        self.raise_error('error_server_internal.json', errors.OneDriveServerInternalError)


class TestOneDriveRecoverableError(unittest.TestCase):
    def test_parse(self):
        error = errors.OneDriveRecoverableError(30)
        self.assertEqual(30, error.retry_after_seconds)


if __name__ == '__main__':
    unittest.main()
