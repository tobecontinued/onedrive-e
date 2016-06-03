import os

from onedrived import OS_HOSTNAME


def append_hostname(path):
    """
    Rename a file "A" to "A (hostname[, count])" to resolve name collisions.
    :param str path: Path to rename.
    :rtype: str
    """
    i = 1
    suffix = ' (' + OS_HOSTNAME + ')'
    p, ext = os.path.splitext(path)
    while os.path.exists(p + suffix + ext):
        suffix = ' ' + str(i) + ' (' + OS_HOSTNAME + ')'
        i += 1
    n = p + suffix + ext
    os.rename(path, n)
    return n


def stat_file(filepath):
    """
    Return the size and mtime of a file.
    :param str filepath: Path of the file to stat.
    :rtype: (int, int)
    """
    return os.path.getsize(filepath), os.path.getmtime(filepath)


def unpack_first_item(q):
    """
    :param dict[str, onedrived.store.items_db.ItemRecord] q: Item dictionary returned by items_db.
    :return:
    """
    key, item = q.popitem()
    q[key] = item
    return key, item
