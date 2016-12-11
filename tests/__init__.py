import json
import logging
import re

try:
    from unittest import mock
except:
    # noinspection PyUnresolvedReferences
    import mock

from onedrivee import get_content as get_content_orig

logging.disable(logging.CRITICAL)
camel_to_underscore = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def get_data(file_name):
    """
    Return a dictionary defined a file in data/.
    :param str file_name: File name in data/.
    :rtype dict[str, T]:
    """
    return json.loads(get_content(file_name, True))


def get_content(file_name, is_text=True):
    """
    Read a resource file in data/.
    :param str file_name: File name in data/.
    :param True | False is_text: True to indicate the text is UTF-8 encoded.
    :return str | bytes: Content of the file.
    """
    return get_content_orig(file_name, 'tests', is_text)


def to_underscore_name(s):
    """
    Convert camelCase to camel_case.
    :param s: The string to convert.
    :rtype: str
    """
    return camel_to_underscore.sub(r'_\1', s).lower()
