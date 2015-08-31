__author__ = 'xb'

import threading

from onedrive_d.store import items_db
from onedrive_d.store import task_pool
from onedrive_d.vendor import rwlock


def get_sample_item_storage_manager():
    return items_db.ItemStorageManager(':memory:')


def get_sample_task_pool():
    p = task_pool.TaskPool()
    p._lock = rwlock.RWLock()
    p._semaphore = threading.Semaphore(0)
    return p
