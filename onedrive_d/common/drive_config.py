__author__ = 'xb'


class DriveConfig:
    DEFAULT_VALUES = {
        'max_get_size_bytes': 1048576,
        'max_put_size_bytes': 524288,
        'local_root': None,
        'ignore_files': {},
        'proxies': {}
    }

    def __init__(self, data):
        for k, v in self.DEFAULT_VALUES.items():
            if k not in data:
                data[k] = v
        if isinstance(data['ignore_files'], list):
            data['ignore_files'] = set(data['ignore_files'])
        for item in self.DEFAULT_VALUES['ignore_files']:
            if item not in data['ignore_files']:
                data['ignore_files'].add(item)
        for k, v in self.DEFAULT_VALUES['proxies'].items():
            if k not in data['proxies']:
                data['proxies'][k] = v
        self._data = data

    @staticmethod
    def default_config():
        return DriveConfig(DriveConfig.DEFAULT_VALUES)

    @classmethod
    def set_default_config(cls, config):
        """
        Set the new config as default, with side-effect of updating all existing configs that use (unsaved) default
        values.
        :param onedrive_d.api.drives.DriveConfig config:
        """
        for k, v in cls.DEFAULT_VALUES.items():
            v2 = getattr(config, k)
            if v2 != v:
                cls.DEFAULT_VALUES[k] = v2

    @property
    def max_get_size_bytes(self):
        """
        :rtype: int
        """
        return self._data['max_get_size_bytes']

    @property
    def max_put_size_bytes(self):
        """
        :rtype: int
        """
        return self._data['max_put_size_bytes']

    @property
    def local_root(self):
        """
        :rtype: str
        """
        return self._data['local_root']

    @property
    def ignore_files(self):
        """
        :rtype: [str]
        """
        return self._data['ignore_files']

    @property
    def proxies(self):
        """
        :rtype: dict[str, str]
        """
        return self._data['proxies']

    def dump(self):
        data = {}
        for key in ['max_get_size_bytes', 'max_put_size_bytes', 'local_root']:
            if getattr(self, key) != self.DEFAULT_VALUES[key]:
                data[key] = getattr(self, key)
        ignore_files = [s for s in self.ignore_files if s not in self.DEFAULT_VALUES['ignore_files']]
        if len(ignore_files) > 0:
            data['ignore_files'] = ignore_files
        proxies = {k: v for k, v in self._data['proxies'].items()
                   if k not in self.DEFAULT_VALUES['proxies'] or v != self.DEFAULT_VALUES['proxies'][k]}
        if len(proxies) > 0:
            data['proxies'] = proxies
        return data

    @classmethod
    def load(cls, d):
        return DriveConfig(d)
