"""
Other classes use this class to generate logger.
"""

import atexit
import logging

logging.basicConfig(format='[%(asctime)-15s] %(levelname)s: %(threadName)s: %(message)s')
atexit.register(logging.shutdown)


def get_logger(name, min_level=logging.DEBUG, path=None):
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(min_level)
    if path is not None:
        logger_fh = logging.FileHandler(path, 'a')
        logger_fh.setLevel(min_level)
        logger.addHandler(logger_fh)
    return logger
