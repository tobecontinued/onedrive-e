from onedrivee.store import items_db
from onedrivee.store import task_pool


def get_sample_item_storage_manager():
    return items_db.ItemStorageManager(':memory:')


def get_sample_task_pool():
    p = task_pool.TaskPool()
    return p
