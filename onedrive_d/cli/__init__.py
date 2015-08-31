__author__ = 'xb'
__all__ = ['cli_main', 'cli_worker', 'pref_main']

import atexit
import os

from onedrive_d import OS_USER_HOME
from onedrive_d.common import user_config
from onedrive_d.store import user_config_db

CONFIG_DIR = OS_USER_HOME + '/.onedrived'
USER_CONF_PATH = CONFIG_DIR + '/user_config.json'


def get_current_user_config():
    if not hasattr(get_current_user_config, '_user_conf'):
        if os.path.exists(USER_CONF_PATH):
            user_conf = user_config_db.load_user_config(USER_CONF_PATH)
        else:
            user_conf = user_config.UserConfig(user_config.UserConfig.DEFAULT_CONFIG)
        atexit.register(user_config_db.save_user_config, USER_CONF_PATH, user_conf)
        setattr(get_current_user_config, '_user_conf', user_conf)
    return getattr(get_current_user_config, '_user_conf')
