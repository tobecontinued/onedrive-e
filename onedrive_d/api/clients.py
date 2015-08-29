"""
OneDrive API client abstraction. Each client holds at least one Account typed object.
"""

from urllib.parse import urlencode


class PersonalClient:
    OAUTH_AUTHORIZE_URI = ''
    OAUTH_AUTH_URL = 'https://login.live.com/oauth20_authorize.srf'
    OAUTH_TOKEN_URI = 'https://login.live.com/oauth20_token.srf'
    OAUTH_SIGN_OUT_URI = 'https://login.live.com/oauth20_logout.srf'
    API_URI = 'https://api.onedrive.com/v1.0'
    DEFAULT_CLIENT_ID = '000000004010C916'
    DEFAULT_CLIENT_SECRET = 'PimIrUibJfsKsMcd0SqwPBwMTV7NDgYi'
    DEFAULT_REDIRECT_URI = 'https://login.live.com/oauth20_desktop.srf'
    DEFAULT_CLIENT_SCOPE = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

    def __init__(self, client_id=DEFAULT_CLIENT_ID, client_secret=DEFAULT_CLIENT_SECRET,
                 client_scope=DEFAULT_CLIENT_SCOPE,
                 redirect_uri=DEFAULT_REDIRECT_URI,
                 proxies=None,
                 net_monitor=None):
        """
        :param str client_id: Client ID for the app.
        :param str client_secret: Client secret for the app.
        :param list[str] client_scope: (Optional) Permissions for the app.
        :param str redirect_uri: Landing URL during authentication process.
        :param dict[str, str] proxies: Proxy settings.
        :param onedrive_d.common.netman.NetworkMonitor net_monitor: The underlying network monitor.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_scope = client_scope
        self.redirect_uri = redirect_uri
        self.accounts = []
        self.proxies = proxies
        self.net_monitor = net_monitor

    def get_auth_uri(self, display='touch', locale='en'):
        params = {
            'client_id': self.client_id,
            'scope': ' '.join(self.client_scope),
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'display': display,
            'locale': locale
        }
        return self.OAUTH_AUTH_URL + '?' + urlencode(params)


class BusinessClient:
    API_URI = ''

    def __init__(self):
        raise NotImplementedError("OneDrive for Business not supported yet.")

    def get_auth_uri(self, locale='en'):
        raise NotImplementedError()
