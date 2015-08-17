__author__ = 'xb'

from onedrive_d.store import items_db
from onedrive_d.store import task_pool


def get_sample_item_storage_manager():
    return items_db.ItemStorageManager(':memory:')


def get_sample_task_pool():
    return task_pool.TaskPool()
