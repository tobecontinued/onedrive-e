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

    def test_auto_renew_tokens(self):
        account = account_factory.get_sample_personal_account()
        url = 'https://test_url'
        normal_data = [(get_data('error_token_expired.json'), requests.codes.forbidden), ({}, requests.codes.ok)]
        new_tokens = get_data('personal_access_token_alt.json')
        with Mocker() as mocker:
            def normal_callback(request, context):
                data, status_code = normal_data.pop(0)
                context.status_code = status_code
                return data

            def renew_callback(request, context):
                body = parse_qs(request.body)
                for k, v in body.items():
                    # parse_qs returns dict[str, [int | str]]
                    self.assertEqual(1, len(v))
                    body[k] = v.pop()
                self.assertEqual(account.client.client_id, body['client_id'])
                self.assertEqual(account.client.client_secret, body['client_secret'])
                self.assertEqual(account.refresh_token, body['refresh_token'])
                self.assertEqual(account.client.redirect_uri, body['redirect_uri'])
                self.assertEqual('refresh_token', body['grant_type'])
                context.status_code = requests.codes.ok
                return new_tokens

            self.assertNotEqual(account.access_token, new_tokens['access_token'])
            self.assertNotEqual(account.refresh_token, new_tokens['refresh_token'])
            mocker.post(url, json=normal_callback)
            mocker.post(account.client.OAUTH_TOKEN_URI, json=renew_callback)
            rest_client = restapi.ManagedRESTClient(session=requests.Session(), net_mon=None, account=account)
            rest_client.post(url)
            self.assertEqual(account.access_token, new_tokens['access_token'])
            self.assertEqual(account.refresh_token, new_tokens['refresh_token'])

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
