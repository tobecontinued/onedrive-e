"""
All facet representations. In this module, we use "_time" for timestamp-related functions, and "_time_str" for ISO-8601
timestamp strings.

https://github.com/OneDrive/onedrive-api-docs/tree/master/facets
"""

from datetime import datetime
from ciso8601 import parse_datetime


class FileSystemInfoFacet:
    """
    The FileSystemInfo facet contains properties that are reported by the device's local file system for the local
    version of an item. This facet can be used to specify the last modified date or created date of the item as it
    was on the local device.

    https://github.com/OneDrive/onedrive-api-docs/blob/master/facets/filesysteminfo_facet.md
    """

    def __init__(self, data):
        self._data = data
        self._created_time = parse_datetime(data['createdDateTime'])
        self._modified_time = parse_datetime(data['lastModifiedDateTime'])

    @property
    def created_time(self):
        """
        :return int: The UNIX timestamp the file was created on a client.
        """
        return self._created_time

    @created_time.setter
    def created_time(self, value):
        """
        :param int value: A UNIX timestamp.
        """
        self._data['createdDateTime'] = datetime.utcfromtimestamp(value)
        self._created_time = value

    @property
    def modified_time(self):
        """
        :return int: The UNIX timestamp the file was last modified on a client.
        """
        return self._modified_time

    @modified_time.setter
    def modified_time(self, value):
        """
        :param int value: A UNIX timestamp.
        """
        self._data['lastModifiedDateTime'] = datetime.utcfromtimestamp(value)
        self.modified_time = value


class HashFacet:
    """
    The Hashes facet groups different types of hashes into a single structure, for an item on OneDrive.
    In some cases hash values may not be available. If this is the case, the hash values on an item will be updated
    after the item is downloaded.

    https://github.com/OneDrive/onedrive-api-docs/blob/master/facets/hashes_facet.md
    """

    def __init__(self, data):
        if 'crc32Hash' not in data:
            data['crc32Hash'] = None
        if 'sha1Hash' not in data:
            data['sha1Hash'] = None
        self._data = data

    @property
    def sha1(self):
        """
        :return str | None: SHA1 hash for the contents of the file (if available)
        """
        return self._data['sha1Hash']

    @property
    def crc32(self):
        """
        :return str | None: The CRC32 value of the file (if available)
        """
        return self._data['crc32Hash']


class FileFacet:
    """
    The File facet groups file-related data on OneDrive into a single structure. It is available on the file property
    of Item resources that represent files.

    https://github.com/OneDrive/onedrive-api-docs/blob/master/facets/file_facet.md
    """

    def __init__(self, data):
        self._data = data

    @property
    def mime_type(self):
        """
        :return str: The MIME type for the file. Determined by logic on the server.
        """
        return self._data['mimeType']

    @property
    def hashes(self):
        """
        :return HashFacet: Hashes of the file's binary content, if available.
        """
        return HashFacet(self._data['hashes'])


class ImageFacet:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/facets/image_facet.md
    """

    def __init__(self, data):
        """
        :param dict[str, int] data: A dictionary representing the dimension of the image
        """
        self.height = data['height']
        self.weight = data['weight']


class PhotoFacet:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/facets/photo_facet.md
    """

    def __init__(self, data):
        self._data = data

    @property
    def taken_time(self):
        """
        :return int: A UNIX timestamp representing the date and time the photo was taken.
        """
        return parse_datetime(self._data['takenDateTime'])

    @property
    def camera_make(self):
        """
        :return str: Camera manufacturer.
        """
        return self._data['cameraMake']

    @property
    def camera_model(self):
        """
        :return str: Camera model.
        """
        return self._data['cameraModel']

    @property
    def f_number(self):
        """
        :return float: The F-stop value from the camera.
        """
        return self._data['fNumber']

    @property
    def exposure_denominator(self):
        """
        :return float: The denominator for the exposure time fraction from the camera.
        """
        return self._data['exposureDenominator']

    @property
    def exposure_numerator(self):
        """
        :return float: The numerator for the exposure time fraction from the camera.
        """
        return self._data['exposureNumerator']

    @property
    def focal_length(self):
        """
        :return float: The focal length from the camera.
        """
        return self._data['focalLength']

    @property
    def iso(self):
        """
        :return float: The ISO value from the camera.
        """
        return self._data['iso']


class FolderFacet:
    def __init__(self, data):
        self._data = data

    def child_count(self):
        """
        :return int: Number of children contained immediately within this container.
        """
        return self._data['childCount']


class QuotaFacet:
    def __init__(self, data):
        self._data = data

    @property
    def total(self):
        """
        Total allowed storage space, in bytes.
        :rtype: int
        """
        return self._data['total']

    @property
    def used(self):
        """
        Total space used, in bytes.
        :rtype: int
        """
        return self._data['used']

    @property
    def remaining(self):
        """
        Total space remaining before reaching the quota limit, in bytes.
        :rtype: int
        """
        return self._data['remaining']

    @property
    def deleted(self):
        """
        Total space consumed by files in the recycle bin, in bytes.
        :rtype: int
        """
        return self._data['deleted']

    @property
    def state(self):
        """
        String that indicates the state of the storage space. {normal, nearing, critical, exceeded}.
        :rtype: str
        """
        return self._data['state']
