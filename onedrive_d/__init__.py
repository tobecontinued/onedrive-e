# encoding: utf-8

"""
onedrive-d is an OneDrive client based on OneDrive API.
It aims to run on major Linux distributions that support Python 3.
"""

__all__ = ['api', 'cli', 'common', 'store', 'tests', 'ui', 'vendor']
__author__ = "Xiangyu Bu"
__copyright__ = "Copyright © 2014-present Xiangyu Bu"
__created__ = "2015-08-07"
__credits__ = []
__email__ = "xybu92@live.com"
__license__ = "GPL 3.0"
__project__ = "onedrive-d"
__status__ = "Development"
__updated__ = "2015-08-08"
__version__ = "2.0.0.dev1"

import os
import pkgutil
from calendar import timegm
from datetime import datetime
from pwd import getpwnam, getpwuid
from ciso8601 import parse_datetime


def get_current_os_user():
    """
    Find the real user who runs the current process. Return a tuple of uid, username, homedir.
    :rtype: (int, str, str)
    """
    user_name = os.getenv('SUDO_USER')
    if not user_name:
        user_name = os.getenv('USER')
    if user_name:
        pw = getpwnam(user_name)
        user_id = pw.pw_uid
    else:
        # If cannot find the user, use ruid instead.
        user_id = os.getresuid()[0]
        pw = getpwuid(user_id)
        user_name = pw.pw_name
    user_home = pw.pw_dir
    return user_id, user_name, user_home


def datetime_to_str(d):
    """
    :param datetime.datetime d:
    :return str:
    """
    return d.isoformat() + 'Z'


def str_to_datetime(s):
    """
    :param str s:
    :return datetime.datetime:
    """
    return parse_datetime(s)


def datetime_to_timestamp(d):
    """
    :param datetime.datetime d: A datetime object.
    :return float: An equivalent UNIX timestamp.
    """
    return timegm(d.utctimetuple()) + d.microsecond / 1e6


def timestamp_to_datetime(t):
    """
    Convert a UNIX timestamp to a datetime object. Precision loss may occur.
    :param float t: A UNIX timestamp.
    :return datetime.datetime: An equivalent datetime object.
    """
    return datetime.utcfromtimestamp(t)


def compare_timestamps(t1, t2):
    if t1 - t2 > 0.001:
        return 1
    elif t2 - t1 > 0.001:
        return -1
    else:
        return 0


def get_content(file_name, pkg_name='onedrive_d', is_text=True):
    """
    Read a resource file in data/.
    :param str file_name:
    :param str pkg_name:
    :param True | False is_text: True to indicate the text is UTF-8 encoded.
    :return str | bytes: Content of the file.
    """
    content = pkgutil.get_data(pkg_name, 'data/' + file_name)
    if is_text:
        content = content.decode('utf-8')
    return content


OS_USER_ID, OS_USER_NAME, OS_USER_HOME = get_current_os_user()
