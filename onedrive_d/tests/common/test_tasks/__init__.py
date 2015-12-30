import os

from onedrive_d.common.tasks import TaskBase
from onedrive_d.tests.api.drive_factory import get_sample_drive_object
from onedrive_d.tests.store.db_factory import get_sample_item_storage_manager
from onedrive_d.tests.store.db_factory import get_sample_task_pool


def setup_os_mock():
    call_hist = {
        'os.rename': [],
        'os.utime': [],
        'os.chown': []
    }
    os.rename = lambda old, new: call_hist['os.rename'].append((old, new))
    os.utime = lambda fp, tt: call_hist['os.utime'].append((fp, tt))
    os.chown = lambda fp, uid, gid: call_hist['os.chown'].append((fp, uid, gid))
    return call_hist


def get_sample_task_base():
    t = TaskBase()
    t.drive = get_sample_drive_object()
    t.items_store = get_sample_item_storage_manager().get_item_storage(t.drive)
    t.task_pool = get_sample_task_pool()
    return t
