__author__ = 'xb'

import logging

from onedrive_d.api import drives
from onedrive_d.common import drive_config
from onedrive_d.common import logger_factory
from onedrive_d.store import account_db
from onedrive_d.store import drives_db


def mock_loggers():
    for cls in [drives.DriveObject, account_db.AccountStorage, account_db.AccountStorage, drives_db.DriveStorage,
                drive_config.DriveConfig]:
        cls.logger = logger_factory.get_logger('ut_' + cls.__name__, min_level=logging.CRITICAL)
