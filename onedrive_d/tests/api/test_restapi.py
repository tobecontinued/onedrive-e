__author__ = 'xb'

import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import requests
from requests_mock import Mocker

from onedrive_d.api import restapi


class TestManagedRESTClient(unittest.TestCase):
    def request_status_code(self, status_code, retry_after_seconds=None):
        uri = 'https://foo/bar'
        rest_client = restapi.ManagedRESTClient(session=requests.Session(), net_mon=None, account=None, proxies=None)
        status_codes = [status_code, requests.codes.ok]

        def callback(request, context):
            context.status_code = status_codes.pop(0)
            if context.status_code == status_code:
                if retry_after_seconds is not None:
                    context.headers['Retry-After'] = str(retry_after_seconds)
                return ''
            else:
                return 'good'
        with Mocker() as mock:
            mock.get(uri, text=callback)
            with patch('time.sleep', autospec=True) as mock_sleep:
                request = rest_client.get(uri)
                self.assertEqual(requests.codes.ok, request.status_code)
                self.assertEqual(0, len(status_codes))
                self.assertEqual('good', request.text)
                if retry_after_seconds is None:
                    retry_after_seconds = restapi.ManagedRESTClient.AUTO_RETRY_SECONDS
                mock_sleep.assert_called_once_with(retry_after_seconds)

    def test_auto_recover_responses(self):
        """
        Test if the API can recover the request when the server returns a status code indicating retry later.
        """
        for status_code in restapi.ManagedRESTClient.RECOVERABLE_STATUS_CODES:
            if status_code == requests.codes.too_many:
                retry_after_seconds = 123
            else:
                retry_after_seconds = None
            self.request_status_code(status_code=status_code, retry_after_seconds=retry_after_seconds)


if __name__ == '__main__':
    unittest.main()
