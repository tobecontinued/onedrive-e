__author__ = 'xb'

from copy import deepcopy

from onedrived.common import logger_factory
from onedrived.common import path_filter


class DriveConfig:
    DEFAULT_VALUES = {
        'max_get_size_bytes': 1048576,
        'max_put_size_bytes': 524288,
        'local_root': None,
        'ignore_files': set(),
    }

    logger = logger_factory.get_logger('DriveConfig')

    def __init__(self, data):
        for k, v in self.DEFAULT_VALUES.items():
            if k not in data:
                data[k] = v
        if isinstance(data['ignore_files'], list):
            data['ignore_files'] = set(data['ignore_files'])
        for item in self.DEFAULT_VALUES['ignore_files']:
            if item not in data['ignore_files']:
                data['ignore_files'].add(item)
        self.data = data

    @staticmethod
    def default_config():
        return DriveConfig(deepcopy(DriveConfig.DEFAULT_VALUES))

    @classmethod
    def set_default_config(cls, config):
        """
        Set the new config as default, with side-effect of updating all existing configs that use (unsaved) default
        values.
        :param onedrived.api.drives.DriveConfig config:
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
        return self.data['max_get_size_bytes']

    @property
    def max_put_size_bytes(self):
        """
        :rtype: int
        """
        return self.data['max_put_size_bytes']

    @property
    def local_root(self):
        """
        :rtype: str
        """
        return self.data['local_root']

    @property
    def ignore_files(self):
        """
        :rtype: [str]
        """
        return self.data['ignore_files']

    # noinspection PyAttributeOutsideInit
    @property
    def path_filter(self):
        if not hasattr(self, '_path_filter'):
            rules = set()
            for path in self.ignore_files:
                try:
                    with open(path, 'r') as f:
                        rules.update(f.read().splitlines())
                except Exception as e:
                    self.logger.error('Failed to load ignore list "%s": %s', path, e)
            self._path_filter = path_filter.PathFilter(rules)
        return self._path_filter

    def dump(self, exact_dump=False):
        data = {}
        for key in ['max_get_size_bytes', 'max_put_size_bytes', 'local_root']:
            if exact_dump or getattr(self, key) != self.DEFAULT_VALUES[key]:
                data[key] = getattr(self, key)
        ignore_files = [s for s in self.ignore_files if exact_dump or s not in self.DEFAULT_VALUES['ignore_files']]
        if len(ignore_files) > 0:
            data['ignore_files'] = ignore_files
        return data

    @classmethod
    def load(cls, d):
        return DriveConfig(d)
