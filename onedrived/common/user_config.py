import json

from onedrived.common.drive_config import DriveConfig


class UserConfig:
    """
    Global settings for a user.
    """

    DEFAULT_CONFIG = {
        'num_consumers': 4,
        'deep_sync_interval_seconds': 300,
        'http_retry_after_seconds': 30,
        'default_drive_config': DriveConfig.default_config(),
        'proxies': dict()
    }

    def __init__(self, data):
        """
        :param dict[str, int | str | onedrived.common.drive_config.DriveConfig] data: Previously dumped user config
        data.
        """
        for k in self.DEFAULT_CONFIG:
            if k not in data:
                data[k] = self.DEFAULT_CONFIG[k]
        self.num_consumers = data['num_consumers']
        self.deep_sync_interval_seconds = data['deep_sync_interval_seconds']
        self.http_retry_after_seconds = data['http_retry_after_seconds']
        self.default_drive_config = data['default_drive_config']
        self.proxies = data['proxies']

    def take_effect(self):
        DriveConfig.set_default_config(self.default_drive_config)

    def dump(self):
        if self.proxies is not None:
            if len(self.proxies) == 0 or self.proxies['https'] == '':
                self.proxies = None
        data = {
            'num_consumers': self.num_consumers,
            'deep_sync_interval_seconds': self.deep_sync_interval_seconds,
            'http_retry_after_seconds': self.http_retry_after_seconds,
            'default_drive_config': self.default_drive_config.dump(exact_dump=True),
            'proxies': self.proxies
        }
        return json.dumps(data)

    @classmethod
    def load(cls, s):
        data = json.loads(s)
        data['default_drive_config'] = DriveConfig.load(data['default_drive_config'])
        return UserConfig(data)
