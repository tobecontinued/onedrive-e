"""
All facet representations. In this module, we use "_time" for timestamp-related functions, and "_time_str" for ISO-8601
timestamp strings.

https://github.com/OneDrive/onedrive-api-docs/tree/master/facets
"""

from ciso8601 import parse_datetime


class FileSystemInfoFacet:
    """
    The FileSystemInfo facet contains properties that are reported by the device's local file system for the local
    version of an item. This facet can be used to specify the last modified date or created date of the item as it
    was on the local device.

    https://github.com/OneDrive/onedrive-api-docs/blob/master/facets/filesysteminfo_facet.md
    """

    def __init__(self, data=None, created_time=None, modified_time=None):
        """
        :param dict[str, str] | None data: A JSON dictionary of FileSystemInfoFacet.
        :param datetime.datetime | None created_time: A datetime object for creation time.
        :param datetime.datetime | None modified_time: A datetime object for last modification time.
        """
        if data is None:
            self.data = {}
            if created_time is not None:
                self.set_datetime('_created_time', 'createdDateTime', created_time)
            if modified_time is not None:
                self.set_datetime('_modified_time', 'lastModifiedDateTime', modified_time)
        else:
            self._created_time = parse_datetime(data['createdDateTime'])
            self._modified_time = parse_datetime(data['lastModifiedDateTime'])
            self.data = data

    def set_datetime(self, prop, key, value):
        """
        Used internally to set a datetime property.
        :param str prop: Object property name.
        :param str key: Dictionary key name.
        :param datetime.datetime value: A UTC datetime object denoting when the file was created on a client.
        """
        setattr(self, prop, value)
        self.data[key] = value.isoformat() + 'Z'

    @property
    def created_time(self):
        """
        :rtype: datetime.datetime
        """
        return self._created_time

    @property
    def modified_time(self):
        """
        :rtype: datetime.datetime
        """
        return self._modified_time


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
        :rtype: str
        """
        return self._data['mimeType']

    @property
    def hashes(self):
        """
        :rtype: HashFacet
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
        self.width = data['width']


class PhotoFacet:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/facets/photo_facet.md
    """

    def __init__(self, data):
        self._data = data

    @property
    def taken_time(self):
        """
        :rtype: int
        """
        return parse_datetime(self._data['takenDateTime'])

    @property
    def camera_make(self):
        """
        :rtype: str
        """
        return self._data['cameraMake']

    @property
    def camera_model(self):
        """
        :rtype: str
        """
        return self._data['cameraModel']

    @property
    def f_number(self):
        """
        :rtype: float
        """
        return self._data['fNumber']

    @property
    def exposure_denominator(self):
        """
        :rtype: float
        """
        return self._data['exposureDenominator']

    @property
    def exposure_numerator(self):
        """
        :rtype: float
        """
        return self._data['exposureNumerator']

    @property
    def focal_length(self):
        """
        :rtype: float
        """
        return self._data['focalLength']

    @property
    def iso(self):
        """
        :rtype: float
        """
        return self._data['iso']


class FolderFacet:
    def __init__(self, data):
        self._data = data

    @property
    def child_count(self):
        """
        :rtype: int
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


class LocationFacet:
    def __init__(self, data):
        """
        :param dict[str, float] data: JSON deserialized location facet dict.
        """
        self._data = data

    @property
    def altitude(self):
        """
        :rtype: float
        """
        return self._data['altitude']

    @property
    def latitude(self):
        """
        :rtype: float
        """
        return self._data['latitude']

    @property
    def longitude(self):
        """
        :rtype: float
        """
        return self._data['longitude']
