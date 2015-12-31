from calendar import timegm
from datetime import datetime

from iso8601 import parse_date


def datetime_to_str(d):
    """
    :param datetime.datetime d:
    :return str:
    """
    return d.isoformat().replace('+00:00', 'Z', 1)


def str_to_datetime(s):
    """
    :param str s:
    :return datetime.datetime:
    """
    return parse_date(s)


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
