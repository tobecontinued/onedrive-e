__author__ = 'xb'

import os


class MockException(Exception):
    pass


def mock_rename(records):
    def rename(old, new):
        records.append((old, new))

    os.rename = rename


def mock_getsize(routing_dict):
    """
    :param dict[str, int] routing_dict:
    """

    def fake_getsize(path):
        if path in routing_dict:
            return routing_dict[path]
        raise MockException('os.path.getsize("{}") is not expected.' % path)

    os.path.getsize = fake_getsize
