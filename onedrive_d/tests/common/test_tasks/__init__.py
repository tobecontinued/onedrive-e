__author__ = 'xb'

from onedrive_d.common import drive_config
from onedrive_d.common import tasks
from onedrive_d.tests.api import drive_factory
from onedrive_d.tests.mocks import mock_os
from onedrive_d.tests.store import db_factory


class BaseTestCase:
    # noinspection PyAttributeOutsideInit
    def setup_objects(self):
        self.rename_records = []
        self.drive = drive_factory.get_sample_drive_object()
        self.drive.config = drive_config.DriveConfig({'max_put_size_bytes': 10})
        self.items_store_mgr = db_factory.get_sample_item_storage_manager()
        self.items_store = self.items_store_mgr.get_item_storage(self.drive)
        self.task_pool = db_factory.get_sample_task_pool()
        self.task_base = tasks.TaskMixin()
        self.task_base.drive = self.drive
        self.task_base.items_store = self.items_store
        self.task_base.task_pool = self.task_pool
        mock_os.mock_rename(self.rename_records)
