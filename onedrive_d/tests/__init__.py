__author__ = 'xb'
__all__ = ['api', 'common']

import json
import pkgutil
import re

camel_to_underscore = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def get_data(file_name):
    """
    Return a dictionary defined a file in data/ directory.
    :param str file_name: File name in "data/" directory.
    :rtype dict[str, T]:
    """
    return json.loads(pkgutil.get_data('onedrive_d.tests', 'data/' + file_name).decode('utf-8'))


def to_underscore_name(s):
    """
    Convert camelCase to camel_case.
    :param s: The string to convert.
    :rtype: str
    """
    return camel_to_underscore.sub(r'_\1', s).lower()
