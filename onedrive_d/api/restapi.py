"""
A RESTful HTTP wrapper based on requests.Session. It wraps HTTP requests so that when a
connection error is detected, the caller thread is suspended and managed by
network monitor.
"""

import time

import requests

from . import errors
from ..common import logger_factory


class ManagedRESTClient:
    AUTO_RETRY_SECONDS = 30
    RECOVERABLE_STATUS_CODES = {requests.codes.too_many, 500, 502, 503, 504}
    logger = logger_factory.get_logger(__name__)

    def __init__(self, session, net_mon, account, proxies=None):
        """
        :param session: Dictate a requests Session object.
        :param onedrive_d.common.netman.NetworkMonitor net_mon: Network monitor instance.
        :param onedrive_d.api.accounts.PersonalAccount | onedrive_d.api.accounts.BusinessAccount account: Account.
        :param dict[str, str] proxies: (Optional) A dictionary of protocol-host pairs.
        :return: No return value.
        """
        self.session = session
        self.net_mon = net_mon
        self.account = account
        self.proxies = proxies

    def request(self, method, url, params, ok_status_code, auto_renew):
        """
        Perform a HTTP request call. Do auto-recover as fits.
        :param str method: One of {GET, POST, PATCH, PUT, DELETE}.
        :param str url: URL of the HTTP request.
        :param dict[str, str | dict | bytes] params: Params to send to the request call.
        :param int ok_status_code: Expected status code for HTTP response.
        :param True | False auto_renew: If True, auto recover the expired token.
        :rtype: requests.Response
        :raise errors.OneDriveError:
        """
        while True:
            try:
                request = getattr(self.session, method)(url, **params)
                if request.status_code != ok_status_code:
                    if request.status_code in self.RECOVERABLE_STATUS_CODES:
                        if 'Retry-After' in request.headers:
                            retry_after_seconds = int(request.headers['Retry-After'])
                        else:
                            retry_after_seconds = self.AUTO_RETRY_SECONDS
                        self.logger.info('Server returned code %d which is assumed recoverable. Retry in %d seconds',
                                         request.status_code, retry_after_seconds)
                        raise errors.OneDriveRecoverableError(retry_after_seconds)
                    raise errors.OneDriveError(request.json())
                return request
            except requests.ConnectionError:
                self.net_mon.suspend_caller()
            except errors.OneDriveRecoverableError as e:
                time.sleep(e.retry_after_seconds)
            except errors.OneDriveTokenExpiredError as e:
                if auto_renew:
                    self.account.renew_tokens()
                else:
                    raise e

    def get(self, url, params=None, headers=None, ok_status_code=requests.codes.ok, auto_renew=True):
        """
        Perform a HTTP GET request.
        :param str url: URL of the HTTP request.
        :param dict[str, T] | None params: (Optional) Dictionary to construct query string.
        :param dict | None headers: (Optional) Additional headers for the HTTP request.
        :param int ok_status_code: (Optional) Expected status code for the HTTP response.
        :param True | False auto_renew: (Optional) If True, auto recover from expired token error or Internet failure.
        :rtype: requests.Response
        """
        args = {'proxies': self.proxies}
        if params is not None:
            args['params'] = params
        if headers is not None:
            args['headers'] = headers
        return self.request('get', url, args, ok_status_code=ok_status_code, auto_renew=auto_renew)

    def post(self, url, data=None, json=None, headers=None, ok_status_code=requests.codes.ok, auto_renew=True):
        """
        Perform a HTTP POST request.
        :param str url: URL of the HTTP request.
        :param dict | None data: (Optional) Data in POST body of the request.
        :param dict | None json: (Optional) Send the dictionary as JSON content in POST body and set proper headers.
        :param dict | None headers: (Optional) Additional headers for the HTTP request.
        :param int ok_status_code: (Optional) Expected status code for the HTTP response.
        :param True | False auto_renew: (Optional) If True, auto recover from expired token error or Internet failure.
        :rtype: requests.Response
        """
        params = {
            'proxies': self.proxies
        }
        if json is not None:
            params['json'] = json
        else:
            params['data'] = data
        if headers is not None:
            params['headers'] = headers
        return self.request('post', url, params, ok_status_code=ok_status_code, auto_renew=auto_renew)

    def patch(self, url, json, ok_status_code=requests.codes.ok, auto_renew=True):
        """
        Perform a HTTP PATCH request.
        :param str url: URL of the HTTP request.
        :param dict json: Send the dictionary as JSON content in POST body and set proper headers.
        :param int ok_status_code: (Optional) Expected status code for the HTTP response.
        :param True | False auto_renew: (Optional) If True, auto recover from expired token error or Internet failure.
        :rtype: requests.Response
        """
        params = {
            'proxies': self.proxies,
            'json': json
        }
        return self.request('patch', url, params, ok_status_code=ok_status_code, auto_renew=auto_renew)

    def put(self, url, data, headers=None, ok_status_code=requests.codes.ok, auto_renew=True):
        """
        Perform a HTTP PUT request.
        :param str url: URL of the HTTP request.
        :param bytes | None data: Binary data to send in the request body.
        :param dict | None headers: Additional headers for the HTTP request.
        :param int ok_status_code: (Optional) Expected status code for the HTTP response.
        :param True | False auto_renew: (Optional) If True, auto recover from expired token error or Internet failure.
        :rtype: requests.Response
        """
        params = {
            'proxies': self.proxies,
            'data': data
        }
        if headers is not None:
            params['headers'] = headers
        return self.request('put', url, params=params,
                            ok_status_code=ok_status_code, auto_renew=auto_renew)

    def delete(self, url, ok_status_code=requests.codes.ok, auto_renew=True):
        """
        Perform a HTTP DELETE request on the specified URL.
        :param str url: URL of the HTTP request.
        :param int ok_status_code: (Optional) Expected status code for the HTTP response.
        :param True | False auto_renew: (Optional) If True, auto recover from expired token error or Internet failure.
        :rtype: requests.Response
        """
        return self.request('delete', url, {'proxies': self.proxies},
                            ok_status_code=ok_status_code, auto_renew=auto_renew)
