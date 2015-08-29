__author__ = 'xb'

import json

from onedrive_d.common.drive_config import DriveConfig


class UserConfig:
    """
    Global settings for a user.
    """

    DEFAULT_CONFIG = {
        'http_retry_after_seconds': 30,
        'default_drive_config': DriveConfig.default_config(),
        'proxies': dict()
    }

    def __init__(self, data):
        """
        :param dict[str, int | str | onedrive_d.common.drive_config.DriveConfig] data: Previously dumped user config
        data.
        """
        for k in self.DEFAULT_CONFIG:
            if k not in data:
                data[k] = self.DEFAULT_CONFIG[k]
        self.http_retry_after_seconds = data['http_retry_after_seconds']
        self.default_drive_config = data['default_drive_config']
        self.proxies = data['proxies']

    def take_effect(self):
        DriveConfig.set_default_config(self.default_drive_config)

    def dump(self):
        if self.proxies is not None and len(self.proxies) == 0:
            self.proxies = None
        data = {
            'http_retry_after_seconds': self.http_retry_after_seconds,
            'default_drive_config': self.default_drive_config.dump(),
            'proxies': self.proxies
        }
        return json.dumps(data)

    @classmethod
    def load(cls, s):
        data = json.loads(s)
        data['default_drive_config'] = DriveConfig.load(data['default_drive_config'])
        return UserConfig(data)
