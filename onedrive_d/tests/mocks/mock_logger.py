__author__ = 'xb'

import logging

from onedrive_d.api import drives
from onedrive_d.common import logger_factory
from onedrive_d.store import account_db
from onedrive_d.store import drives_db


def mock_loggers():
    drives.DriveObject.logger = logger_factory.get_logger('ut_DriveObject', min_level=logging.CRITICAL)
    account_db.AccountStorage.logger = logger_factory.get_logger('ut_AccountStorage', min_level=logging.CRITICAL)
    drives_db.DriveStorage.logger = logger_factory.get_logger('ut_DriveStorage', min_level=logging.CRITICAL)
