__author__ = 'xb'

from urllib.parse import parse_qs
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import requests
from requests_mock import Mocker

from onedrive_d.api import errors
from onedrive_d.api import restapi
from onedrive_d.tests import get_data
from onedrive_d.tests.api import account_factory


class TestManagedRESTClient(unittest.TestCase):
    @patch('time.sleep', autospec=True)
    @Mocker()
    def request_status_code(self, mock_sleep, mock_request, status_code, retry_after_seconds=None):
        uri = 'https://foo/bar'
        rest_client = restapi.ManagedRESTClient(session=requests.Session(), net_mon=None, account=None, proxies=None)
        status_codes = [status_code, requests.codes.ok]

        def callback(req, context):
            context.status_code = status_codes.pop(0)
            if context.status_code == status_code:
                if retry_after_seconds is not None:
                    context.headers['Retry-After'] = str(retry_after_seconds)
                return ''
            else:
                return 'good'

        mock_request.get(uri, text=callback)
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

    def assert_compare(self, assert_call, obj, dict, keys):
        for k in keys:
            assert_call(getattr(obj, k), dict[k], k)

    @Mocker()
    def test_auto_renew_tokens(self, mocker):
        account = account_factory.get_sample_personal_account()
        url = 'https://test_url'
        normal_data = [(get_data('error_token_expired.json'), requests.codes.forbidden), ({}, requests.codes.ok)]
        new_tokens = get_data('personal_access_token_alt.json')

        def normal_callback(request, context):
            data, status_code = normal_data.pop(0)
            context.status_code = status_code
            return data

        def renew_callback(request, context):
            body = parse_qs(request.body)  # parse_qs returns dict[str, [int | str]]
            for k, v in body.items():
                self.assertEqual(1, len(v))
                body[k] = v.pop()
            self.assert_compare(self.assertEqual, account.client, body, ['client_id', 'client_secret', 'redirect_uri'])
            self.assertEqual(account.refresh_token, body['refresh_token'])
            self.assertEqual('refresh_token', body['grant_type'])
            context.status_code = requests.codes.ok
            return new_tokens

        compares = ['access_token', 'refresh_token', 'token_type']
        self.assert_compare(self.assertNotEqual, account, new_tokens, compares)
        mocker.post(url, json=normal_callback)
        mocker.post(account.client.OAUTH_TOKEN_URI, json=renew_callback)
        rest_client = restapi.ManagedRESTClient(session=requests.Session(), net_mon=None, account=account)
        rest_client.post(url)
        self.assert_compare(self.assertEqual, account, new_tokens, compares)

    @Mocker()
    def test_raise_token_expired_error(self, mock_request):
        def callback(request, context):
            context.status_code = requests.codes.bad
            return get_data('error_token_expired.json')

        account = account_factory.get_sample_personal_account()
        rest_client = restapi.ManagedRESTClient(session=requests.Session(), net_mon=None, account=account)
        mock_request.get('https://test_url', json=callback)
        self.assertRaises(errors.OneDriveTokenExpiredError, rest_client.get, url='https://test_url', auto_renew=False)

if __name__ == '__main__':
    unittest.main()
