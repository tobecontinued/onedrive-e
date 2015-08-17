__author__ = 'xb'

import os


def mock_rename(records):
    def rename(old, new):
        records.append((old, new))

    os.rename = rename
