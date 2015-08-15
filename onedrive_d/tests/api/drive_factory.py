__author__ = 'xb'

from onedrive_d.api import drives
from onedrive_d.tests import get_data
from onedrive_d.tests.api import account_factory


def get_sample_drive_root():
    account = account_factory.get_sample_personal_account()
    return drives.DriveRoot(account)


def get_sample_drive_object(data=get_data('drive.json')):
    d = drives.DriveObject(root=get_sample_drive_root(), data=data)
    d.local_root = '/tmp'
    return d
