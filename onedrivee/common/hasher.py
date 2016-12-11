import hashlib
import zlib
import sys


def hash_value(file_path, block_size=1048576, algorithm=None):
    """
    Calculate the MD5 or SHA hash value of the data of the specified file.
    :param str file_path:
    :param int block_size:
    :param algorithm: A hash function defined in hashlib.
    :return str:
    """
    if algorithm is None:
      algorithm=hashlib.sha1()
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
    NOTE: this function's result equals to other software generated.
    but not equals to the value got by onedrive.
    So we should use this function in our system.
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
    return format(crc & 0xFFFFFFFF, '08x').upper()
