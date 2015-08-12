__author__ = 'xb'

import threading
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import requests
import requests_mock

from onedrive_d.api import restapi
from onedrive_d.common import netman


@requests_mock.Mocker()
class TestNetworkMonitor(unittest.TestCase):

    @patch('time.sleep', autospec=True)
    def test_suspension(self, mock_request, mock_sleep):
        """
        :param requests_mock.Mocker mock_request:
        :param unittest.mock.patch mock_sleep:
        """
        test_url = 'https://test_url'
        nettest_errors = [requests.ConnectionError, requests.ConnectionError]
        restapi_errors = [requests.ConnectionError]

        def nettest_callback(request, context):
            if len(nettest_errors) > 0:
                error = nettest_errors.pop()
                raise error()
            return ''

        def restapi_callback(request, context):
            if len(restapi_errors) > 0:
                raise restapi_errors.pop()
            context.status_code = requests.codes.ok
            return ''

        netmon = netman.NetworkMonitor()
        mock_request.head(netmon.test_uri, text=nettest_callback)
        mock_request.post(test_url, text=restapi_callback)
        netmon.start()
        rest_cli = restapi.ManagedRESTClient(session=requests.Session(), net_mon=netmon, account=None)
        t = threading.Thread(target=rest_cli.post, kwargs={'url': test_url})
        t.start()
        t.join(timeout=3)
        self.assertEqual(0, len(nettest_errors))
        self.assertEqual(0, len(restapi_errors))
        self.assertEqual(2, mock_sleep.call_count)
        mock_sleep.assert_called_with(netmon.retry_delay)


if __name__ == '__main__':
    unittest.main()
