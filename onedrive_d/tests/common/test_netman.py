__author__ = 'xb'

import threading
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import requests
import requests_mock
from onedrive_d.common import netman


@requests_mock.Mocker()
class TestNetworkMonitor(unittest.TestCase):
    @patch('time.sleep', autospec=True)
    def test_suspension(self, mock_request, mock_sleep):
        """
        :param Mocker mock_request:
        """
        errors = [requests.ConnectionError, requests.ConnectionError]

        def callback(request, context):
            if len(errors) > 0:
                error = errors.pop()
                raise error()
            return ''

        netmon = netman.NetworkMonitor()
        mock_request.head(netmon.test_uri, text=callback)
        netmon.start()
        t = threading.Thread(target=netmon.suspend_caller)
        t.start()
        t.join(timeout=5)
        self.assertEqual(0, len(errors))
        self.assertEqual(2, mock_sleep.call_count)
        mock_sleep.assert_called_with(netmon.retry_delay)


if __name__ == '__main__':
    unittest.main()
