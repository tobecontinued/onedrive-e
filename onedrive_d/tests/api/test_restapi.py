__author__ = 'xb'

import unittest

import requests
from requests_mock import Mocker

from onedrive_d.api import restapi


class TestManagedRESTClient(unittest.TestCase):
    def test_too_many_requests(self):
        uri = 'https://foo/bar'
        rest_client = restapi.ManagedRESTClient(session=requests.Session(), net_mon=None, account=None, proxies=None)
        status_codes = [requests.codes.too_many, requests.codes.ok]
        with Mocker() as mock:
            def callback(request, context):
                context.status_code = status_codes.pop(0)
                context.headers['Retry-After'] = '0'
                return ''

            mock.get(uri, text=callback)
            rest_client.get(uri)


if __name__ == '__main__':
    unittest.main()
