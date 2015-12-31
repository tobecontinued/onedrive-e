import hashlib
import zlib


def hash_value(file_path, block_size=1048576, algorithm=hashlib.sha1()):
    """
    Calculate the MD5 or SHA hash value of the data of the specified file.
    :param str file_path:
    :param int block_size:
    :param algorithm: A hash function defined in hashlib.
    :return str:
    """
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            algorithm.update(data)
    return algorithm.hexdigest().upper()


def crc32_value(file_path, block_size=1048576):
    """
    Calculate the CRC32 value of the data of the specified file.
    :param str file_path:
    :param int block_size:
    :return int:
    """
    crc = 0
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            crc = zlib.crc32(data, crc)
    return str(crc).upper()
