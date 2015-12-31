from onedrived.common.tasks import TaskBase as _TaskBase
from tests.factory.db_factory import get_sample_item_storage_manager as _get_storage_manager
from tests.factory.db_factory import get_sample_task_pool as _get_task_pool
from tests.factory.drive_factory import get_sample_drive_object as _get_drive


def get_sample_task_base():
    t = _TaskBase()
    t.drive = _get_drive()
    t.items_store = _get_storage_manager().get_item_storage(t.drive)
    t.task_pool = _get_task_pool()
    return t
