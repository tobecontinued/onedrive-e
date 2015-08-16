__author__ = 'xb'

import atexit


def register(func, **kwargs):
    pass


def mock_register():
    atexit.register = register
