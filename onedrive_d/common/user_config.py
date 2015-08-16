__author__ = 'xb'

import json
import os
from pwd import getpwnam, getpwuid

from onedrive_d.common.drive_config import DriveConfig


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
    return user_id, user_name, user_home


class UserConfig:
    """
    Global settings for a user.
    """

    DEFAULT_CONFIG = {
        'http_retry_after_seconds': 30,
        'default_drive_config': DriveConfig.default_config()
    }

    def __init__(self, data):
        """
        :param dict[str, int | str | dict] data: Previously dumped user config data.
        """
        for k in self.DEFAULT_CONFIG:
            if k not in data:
                data[k] = self.DEFAULT_CONFIG[k]
        self.http_retry_after_seconds = data['http_retry_after_seconds']
        self.default_drive_config = data['default_drive_config']

    def take_effect(self):
        DriveConfig.set_default_config(self.default_drive_config)

    def dump(self):
        data = {
            'http_retry_after_seconds': self.http_retry_after_seconds,
            'default_drive_config': self.default_drive_config.dump()
        }
        return json.dumps(data)

    @classmethod
    def load(cls, s):
        data = json.loads(s)
        data['default_drive_config'] = DriveConfig.load(data['default_drive_config'])
        return UserConfig(data)
