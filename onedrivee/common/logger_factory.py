"""
Other classes use this class to generate logger.
"""

import atexit
import logging
import logging.handlers

_instance = None


def init_logger(min_level=logging.WARNING, path=None, max_bytes=10 << 100):
    global _instance
    logging.basicConfig(format='[%(asctime)-15s] (%(levelname)s) %(threadName)s: %(message)s')
    _instance = logging.getLogger()
    _instance.propagate = False
    _instance.setLevel(min_level)
    if path:
        handler = logging.handlers.RotatingFileHandler(path, 'a', maxBytes=max_bytes)
        _instance.addHandler(handler)
    atexit.register(logging.shutdown)


def get_logger(name):
    if _instance is None:
        init_logger()
    return _instance
