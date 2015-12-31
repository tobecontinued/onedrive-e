"""
All facet representations. In this module, we use "_time" for timestamp-related functions, and "_time_str" for ISO-8601
timestamp strings.

https://github.com/OneDrive/onedrive-api-docs/tree/master/facets
"""

from onedrived import datetime_to_str, str_to_datetime
from onedrived.api import resources


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
            self._created_time = str_to_datetime(data['createdDateTime'])
            self._modified_time = str_to_datetime(data['lastModifiedDateTime'])
            self.data = data

    def set_datetime(self, prop, key, value):
        """
        Used internally to set a datetime property.
        :param str prop: Object property name.
        :param str key: Dictionary key name.
        :param datetime.datetime value: A UTC datetime object denoting when the file was created on a client.
        """
        setattr(self, prop, value)
        self.data[key] = datetime_to_str(value)

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
        return HashFacet(self._data['hashes']) if 'hashes' in self._data else None


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
        Represents the date and time the photo was taken.
        :rtype: int
        """
        return str_to_datetime(self._data['takenDateTime'])

    @property
    def camera_make(self):
        """
        Camera manufacturer.
        :rtype: str
        """
        return self._data['cameraMake']

    @property
    def camera_model(self):
        """
        Camera model.
        :rtype: str
        """
        return self._data['cameraModel']

    @property
    def f_number(self):
        """
        The F-stop value from the camera.
        :rtype: float
        """
        return self._data['fNumber']

    @property
    def exposure_denominator(self):
        """
        The denominator for the exposure time fraction from the camera.
        :rtype: float
        """
        return self._data['exposureDenominator']

    @property
    def exposure_numerator(self):
        """
        The numerator for the exposure time fraction from the camera.
        :rtype: float
        """
        return self._data['exposureNumerator']

    @property
    def focal_length(self):
        """
        The focal length from the camera.
        :rtype: float
        """
        return self._data['focalLength']

    @property
    def iso(self):
        """
        The ISO value from the camera.
        :rtype: float
        """
        return self._data['iso']


class FolderFacet:
    def __init__(self, data):
        self._data = data

    @property
    def child_count(self):
        """
        Number of children contained immediately within this container.
        :rtype: int
        """
        return self._data['childCount']


class AudioFacet:
    def __init__(self, data):
        self._data = data

    @property
    def album(self):
        """
        The title of the album for this audio file.
        :rtype: str
        """
        return self._data['album']

    @property
    def album_artist(self):
        """
        The artist named on the album for the audio file.
        :rtype: str
        """
        return self._data['albumArtist']

    @property
    def artist(self):
        """
        The performing artist for the audio file.
        :rtype: str
        """
        return self._data['artist']

    @property
    def bitrate(self):
        """
        Bitrate expressed in kbps.
        :rtype: int
        """
        return self._data['bitrate']

    @property
    def composers(self):
        """
        The name of the composer of the audio file.
        :rtype: str
        """
        return self._data['composers']

    @property
    def copyright(self):
        """
        Copyright information for the audio file.
        :rtype: str
        """
        return self._data['copyright']

    @property
    def disc(self):
        """
        The number of the disc this audio file came from.
        :rtype: int
        """
        return self._data['disc']

    @property
    def disc_count(self):
        """
        The total number of discs in this album.
        :rtype: int
        """
        return self._data['discCount']

    @property
    def duration(self):
        """
        Duration of the audio file, expressed in milliseconds
        :rtype: int
        """
        return self._data['duration']

    @property
    def genre(self):
        """
        The genre of this audio file.
        :rtype: str
        """
        return self._data['genre']

    @property
    def has_drm(self):
        """
        Indicates if the file is protected with digital rights management.
        :rtype: True | False
        """
        return self._data['hasDrm']

    @property
    def is_variable_bitrate(self):
        """
        Indicates if the file is encoded with a variable bitrate.
        :rtype: True | False
        """
        return self._data['isVariableBitrate']

    @property
    def title(self):
        """
        The title of the audio file.
        :rtype: str
        """
        return self._data['title']

    @property
    def track(self):
        """
        The number of the track on the original disc for this audio file.
        :rtype: int
        """
        return self._data['track']

    @property
    def track_count(self):
        """
        The total number of tracks on the original disc for this audio file.
        :rtype: int
        """
        return self._data['trackCount']

    @property
    def year(self):
        """
        The year the audio file was recorded.
        :rtype: int
        """
        return self._data['year']


class VideoFacet:
    def __init__(self, data):
        self._data = data

    @property
    def bitrate(self):
        """
        Bit rate of the video in bits per second.
        :rtype: int
        """
        return self._data['bitrate']

    @property
    def duration(self):
        """
        Duration of the file in milliseconds.
        :rtype: int
        """
        return self._data['duration']

    @property
    def height(self):
        """
        Height of the video, in pixels.
        :rtype: int
        """
        return self._data['height']

    @property
    def width(self):
        """
        Width of the video, in pixels.
        :rtype: int
        """
        return self._data['width']


class DeletedFacet:
    """
    Indicates that the item on OneDrive has been deleted. OneDrive API v1.0 has no properties in it.
    """

    def __init__(self, data):
        self._data = data


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


class SharingLinkFacet:
    def __init__(self, data):
        self._data = data

    @property
    def token(self):
        """
        The access token that represents the current link permission. You can use this in place of
        other authentication tokens to access the resource the current permission is set for.
        :rtype: str
        """
        return self._data['token']

    @property
    def web_url(self):
        """
        A URL that opens the item in the browser on the OneDrive website.
        :rtype: str
        """
        return self._data['webUrl']

    @property
    def type(self):
        """
        The type of the link created.
        :rtype: str
        """
        return self._data['type']

    @property
    def read_only(self):
        """
        A view-only sharing link, allowing read-only access.
        :rtype: True | False
        """
        return self.type == 'view'

    @property
    def read_write(self):
        """
        An edit sharing link, allowing read-write access.
        :rtype: True | False
        """
        return self.type == 'edit'

    @property
    def application(self):
        """
        The app the link is associated with. The value is missing or `null` if the link is
        associated with an official Microsoft app.
        :rtype: resources.Identity
        """
        return resources.Identity(self._data['application'])


class PermissionFacet:
    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        """
        The unique identifier of the permission among all permissions on the item.
        :rtype: str
        """
        return self._data['id']

    @property
    def roles(self):
        """
        The type of permission. A sublist of {read, write}
        :rtype: [str]
        """
        return self._data['roles']

    @property
    def can_read(self):
        """
        If the permission allows for reading.
        :rtype: True | False
        """
        return 'read' in self._data['roles']

    @property
    def can_write(self):
        """
        If the permission allows for writing.
        :rtype: True | False
        """
        return 'write' in self._data['roles']

    @property
    def link(self):
        """
        Provides the link details of the current permission, if it is a link type permissions.
        :rtype: SharingLinkFacet
        """
        return SharingLinkFacet(self._data['link'])

    @property
    def inherited_from(self):
        """
        Provides a reference to the ancestor of the current permission, if it is inherited from an
        ancestor.
        :rtype: resources.ItemReference
        """
        return resources.ItemReference(self._data['inheritedFrom'])


class SpecialFolderFacet:
    def __init__(self, data):
        self._data = data

    @property
    def name(self):
        """
        The unique identifier for this item in the `/drive/special` collection
        :rtype: str
        """
        return self._data['name']
