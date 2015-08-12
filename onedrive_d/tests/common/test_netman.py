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
    test_url = 'https://test_url'

    def get_callback(self, max_counter):
        def callback(request, context):
            callback.counter -= 1
            self.assertGreaterEqual(callback.counter, -1)
            if callback.counter >= 0:
                raise requests.ConnectionError()
            return ''

        callback.counter = max_counter
        return callback

    @patch('time.sleep', autospec=True)
    def test_suspension(self, mock_request, mock_sleep):
        """
        :param requests_mock.Mocker mock_request:
        :param unittest.mock.patch mock_sleep:
        """
        netmon = netman.NetworkMonitor()
        mock_request.head(netmon.test_uri, text=self.get_callback(2))
        mock_request.post(self.test_url, text=self.get_callback(1))
        netmon.start()
        rest_cli = restapi.ManagedRESTClient(session=requests.Session(), net_mon=netmon, account=None)
        t = threading.Thread(target=rest_cli.post, kwargs={'url': self.test_url})
        t.start()
        t.join(timeout=2)
        self.assertEqual(2, mock_sleep.call_count)
        mock_sleep.assert_called_with(netmon.retry_delay)


if __name__ == '__main__':
    unittest.main()
