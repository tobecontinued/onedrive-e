__author__ = 'xb'
__all__ = ['api', 'common']

import json
import pkgutil


def get_data(file_name):
    """
    Return a dictionary defined a file in data/ directory.
    :param str file_name: File name in "data/" directory.
    :rtype dict[str, T]:
    """
    return json.loads(pkgutil.get_data('onedrive_d.tests', 'data/' + file_name).decode('utf-8'))
