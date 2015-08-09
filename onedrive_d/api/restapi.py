"""
A RESTful HTTP wrapper based on requests.Session. It wraps HTTP requests so that when a
connection error is detected, the caller thread is suspended and managed by
network monitor.
"""

import requests

from . import errors


class ManagedRESTClient:
    def __init__(self, session, net_mon, account, proxies=None):
        """
        :param session: Dictate a requests Session object.
        :param onedrive_d.common.netman.NetworkMonitor net_mon: Network monitor instance.
        :param onedrive_d.api.accounts.PersonalAccount | onedrive_d.api.accounts.BusinessAccount account: Account.
        :param dict[str, str] proxies: (Optional) A dictionary of protocol-host pairs.
        :return: No return value.
        """
        if session is None:
            session = requests.Session()
        self.session = session
        self.net_mon = net_mon
        self.account = account
        self.proxies = proxies

    def request(self, method, url, params, ok_status_code, auto_renew):
        while True:
            try:
                request = getattr(self.session, method)(url, **params)
                if request.status_code != ok_status_code:
                    raise errors.OneDriveError(request.json())
                return request
            except requests.ConnectionError:
                self.net_mon.suspend_caller()
            except errors.OneDriveTokenExpiredError as e:
                if auto_renew:
                    self.account.renew_tokens()
                else:
                    raise e

    def get(self, url, params=None, headers=None, ok_status_code=requests.codes.ok, auto_renew=True):
        args = {'proxies': self.proxies}
        if params is not None:
            args['params'] = params
        if headers is not None:
            args['headers'] = headers
        return self.request('get', url, args, ok_status_code=ok_status_code, auto_renew=auto_renew)

    def post(self, url, data=None, json=None, ok_status_code=requests.codes.ok, auto_renew=True):
        params = {
            'proxies': self.proxies
        }
        if json is not None:
            params['json'] = json
        else:
            params['data'] = data
        return self.request('post', url, params, ok_status_code=ok_status_code, auto_renew=auto_renew)

    def patch(self, url, json, ok_status_code=requests.codes.ok, auto_renew=True):
        params = {
            'proxies': self.proxies,
            'json': json
        }
        return self.request('patch', url, params, ok_status_code=ok_status_code, auto_renew=auto_renew)

    def put(self, url, data, headers=None, ok_status_code=requests.codes.ok, auto_renew=True):
        params = {
            'proxies': self.proxies,
            'data': data
        }
        if headers is not None:
            params['headers'] = headers
        return self.request('put', url, params=params,
                            ok_status_code=ok_status_code, auto_renew=auto_renew)

    def delete(self, url, ok_status_code=requests.codes.ok, auto_renew=True):
        return self.request('delete', url, {'proxies': self.proxies},
                            ok_status_code=ok_status_code, auto_renew=auto_renew)
