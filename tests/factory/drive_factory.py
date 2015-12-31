from onedrived.api import drives
from onedrived.common import drive_config
from tests import get_data
from tests.factory import account_factory


def get_sample_drive_root():
    account = account_factory.get_sample_personal_account()
    return drives.DriveRoot(account)


def get_sample_drive_object(data=get_data('drive.json')):
    d = drives.DriveObject(
            root=get_sample_drive_root(), data=data, config=drive_config.DriveConfig(get_data('drive_config.json')))
    return d
