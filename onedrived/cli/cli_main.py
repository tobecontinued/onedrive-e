import argparse
import logging
import os
import sys
import time

from onedrived.api import clients
from onedrived.cli import CONFIG_DIR, get_current_user_config
from onedrived.common import logger_factory, netman, task_worker
from onedrived.common.tasks import TaskBase
from onedrived.common.tasks.merge_task import MergeDirTask
from onedrived.store import account_db, drives_db, items_db, task_pool

logger = None
user_conf = None
personal_client = None
business_client = None
account_store = None
drive_store = None
task_store = None
item_store_mgr = None
network_monitor = netman.NetworkMonitor()


def parse_args():
    argparser = argparse.ArgumentParser('onedrived', description='CLI daemon of onedrive-d.')
    argparser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                           default='DEBUG', help='Set the minimum logging level.')
    argparser.add_argument('--log-file', default=None, required=False, help='Store program logs in the specified file.')
    return argparser.parse_args()


def fix_log_args(args):
    try:
        if args.log_file is not None:
            with open(args.log_file, 'w'):
                pass
    except (OSError, IOError) as e:
        print('Cannot open log file "%s": %s. Use stderr.' % (args.log_file, str(e)), file=sys.stderr)
        args.log_file = None
    logger_factory.init_logger(min_level=getattr(logging, args.log_level), path=args.log_file)
    return args


def add_initial_tasks():
    all_drives = drive_store.get_all_drives()
    for key, drive in all_drives.items():
        # root_item = drive.get_root_dir(list_children=False)
        # print(root_item._data)
        base = TaskBase(None)
        base.drive = drive
        base.items_store = item_store_mgr.get_item_storage(drive)
        base.task_pool = task_store
        task = MergeDirTask(base, '', '')
        if not task_store.has_pending_task(task.local_path):
            task_store.add_task(task)


def load_item_storage():
    global item_store_mgr
    item_store_mgr = items_db.ItemStorageManager(CONFIG_DIR)


def load_task_storage():
    global task_store
    task_store = task_pool.TaskPool.get_instance()


def load_user_config():
    global personal_client, business_client, user_conf
    global account_store, drive_store
    user_conf = get_current_user_config()
    user_conf.take_effect()
    network_monitor.start()
    personal_client = clients.PersonalClient(proxies=user_conf.proxies, net_monitor=network_monitor)
    business_client = None
    account_store = account_db.AccountStorage(CONFIG_DIR + '/accounts.db',
                                              personal_client=personal_client, business_client=business_client)
    drive_store = drives_db.DriveStorage(CONFIG_DIR + '/drives.db', account_store)
    account_store.get_all_accounts()


def check_config_dir():
    if not os.path.isdir(CONFIG_DIR):
        logger.critical('Configuration directory "%s" does not exist. Please run `onedrived-pref` first.', CONFIG_DIR)
        sys.exit(1)


def start_task_workers():
    for i in range(user_conf.num_consumers):
        t = task_worker.TaskConsumer(task_pool=task_store)
        t.name = 'W' + str(i)
        t.start()


def refill_tasks():
    try:
        while True:
            logger.info('Refilling initial tasks...')
            add_initial_tasks()
            time.sleep(5 * 60)
    except (KeyboardInterrupt, InterruptedError):
        logger.info('Exiting...')
        sys.exit(0)


def main():
    global logger
    args = fix_log_args(parse_args())
    logger = logger_factory.get_logger('Main')
    check_config_dir()
    load_user_config()
    load_item_storage()
    load_task_storage()
    start_task_workers()
    refill_tasks()


if __name__ == '__main__':
    main()
