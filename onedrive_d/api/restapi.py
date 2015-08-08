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

    def get(self, url, params=None, ok_status_code=requests.codes.ok, auto_renew=True):
        while True:
            try:
                request = self.session.get(url, params=params, proxies=self.proxies)
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

    def post(self, url, data=None, ok_status_code=requests.codes.ok, auto_renew=True):
        while True:
            try:
                request = self.session.post(url, data=data, proxies=self.proxies)
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

    def put(self, url, data, ok_status_code=requests.codes.ok, auto_renew=True):
        pass

    def delete(self, url, data, ok_status_code=requests.codes.ok, auto_renew=True):
        pass
