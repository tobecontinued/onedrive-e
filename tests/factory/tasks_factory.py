from onedrived.common.tasks import TaskBase
from tests.factory.db_factory import get_sample_item_storage_manager
from tests.factory.db_factory import get_sample_task_pool
from tests.factory.drive_factory import get_sample_drive_object


def get_sample_task_base():
    t = TaskBase()
    t.drive = get_sample_drive_object()
    t.items_store = get_sample_item_storage_manager().get_item_storage(t.drive)
    t.task_pool = get_sample_task_pool()
    return t
