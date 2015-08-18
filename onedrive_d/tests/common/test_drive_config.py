__author__ = 'xb'

import os
import sys
import unittest

from onedrive_d.common import drive_config
from onedrive_d.common import path_filter
from onedrive_d.tests import assert_factory
from onedrive_d.tests import get_data
from onedrive_d.tests.mocks import mock_logger

mock_logger.mock_loggers()


class TestDriveConfig(unittest.TestCase):
    data = get_data('drive_config.json')
    conf = drive_config.DriveConfig(data)

    def test_parse(self):
        assert_factory.assert_dict_equals_attributes(self, self.data, self.conf)

    def test_append_default_values(self):
        del self.data['max_get_size_bytes']
        conf = drive_config.DriveConfig(self.data)
        self.assertEqual(drive_config.DriveConfig.DEFAULT_VALUES['max_get_size_bytes'], conf.max_get_size_bytes)

    def test_serialize(self):
        dump = self.conf.dump()
        new_conf = drive_config.DriveConfig(dump)
        for k, v in self.data.items():
            self.assertEqual(v, getattr(new_conf, k))

    def test_set_default_config(self):
        """
        Test both setting default config and differential dumping / loading.
        """
        drive_config.DriveConfig.set_default_config(self.conf)
        data = dict(self.data)
        data['ignore_files'] = set(data['ignore_files'])
        data['ignore_files'].add('/q')
        data['proxies'] = {'sock5': '1.2.3.4:5'}
        conf2 = drive_config.DriveConfig(data)
        dump2 = conf2.dump()
        self.assertDictEqual({'ignore_files': ['/q'], 'proxies': {'sock5': '1.2.3.4:5'}}, dump2)
        conf3 = drive_config.DriveConfig.load(dump2)
        for k in self.data:
            self.assertEqual(getattr(conf2, k), getattr(conf3, k))

    def test_path_filter(self):
        """
        Test if the path filter object is properly instantiated.
        """
        config = drive_config.DriveConfig({
            'ignore_files': [
                os.path.dirname(sys.modules['onedrive_d.tests'].__file__) + '/data/ignore_list.txt',
                '/tmp/foo'  # bad path should not crash the program
            ]
        })
        filter = config.path_filter
        self.assertIsInstance(filter, path_filter.PathFilter)
        self.assertTrue(filter.should_ignore('/foo'))
        self.assertTrue(filter.should_ignore('/a.swp'))


if __name__ == '__main__':
    unittest.main()
