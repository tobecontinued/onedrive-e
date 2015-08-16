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

import pkgutil


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
