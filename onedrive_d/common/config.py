__author__ = 'xb'

import os
from pwd import getpwnam, getpwuid


def get_current_os_user():
    """
    Find the real user who runs the current process. Return a tuple of uid, username, homedir.
    :rtype: (int, str, str)
    """
    user_name = os.getenv('SUDO_USER')
    if not user_name:
        user_name = os.getenv('USER')
    if user_name:
        pw = getpwnam(user_name)
        user_id = pw.pw_uid
    else:
        # If cannot find the user, use ruid instead.
        user_id = os.getresuid()[0]
        pw = getpwuid(user_id)
        user_name = pw.pw_name
    user_home = pw.pw_dir
    return (user_id, user_name, user_home)


class UserConfig:
    http_max_get_size_bytes = 1024000
    http_max_put_size_bytes = 512000
    http_retry_after_seconds = 30
    ignore_files = []
    proxies = None

    def __init__(self, data):
        """
        :param dict[str, int | str | dict[str, str]] data:
        """
        for k in ['http_max_get_size_bytes', 'http_max_put_size_bytes', 'http_retry_after_seconds',
                  'http_retry_after_seconds', 'ignore_files', 'proxies']:
            if k not in data:
                data[k] = getattr(UserConfig, k)
        self.data = data

    @property
    def http_max_get_size_bytes(self):
        """
        The max size, in bytes, for a single HTTP GET call when downloading files.
        :rtype: int
        """
        return self.data['http_max_get_size_bytes']

    @property
    def http_max_put_size_bytes(self):
        """
        The max size, in bytes, for a single HTTP PUT call when uploading files.
        :rtype: int
        """
        return self.data['http_max_put_size_bytes']

    @property
    def http_retry_after_seconds(self):
        """
        The amount of time, in seconds, to wait before retrying a request interrupted by connection error.
        :rtype: int
        """
        return self.data['http_retry_after_seconds']

    @property
    def ignore_files(self):
        """
        The list of registered ignore file paths.
        :rtype: [str]
        """
        return self.data['ignore_files']

    @property
    def proxies(self):
        """
        The dictionary of registered proxies.
        :rtype: dict[str, str]
        """
        return self.data['proxies']
