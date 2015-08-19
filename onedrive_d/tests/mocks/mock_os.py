__author__ = 'xb'

import os


class MockException(Exception):
    pass


def mock_rename(records):
    def rename(old, new):
        records.append((old, new))

    os.rename = rename


def mock_utime(records):
    def utime(path, times):
        records[path] = times

    os.utime = utime
