from ciso8601 import parse_datetime

from . import identities
from . import resources
from . import facets


class OneDriveItemTypes:
    FILE = 'file'
    FOLDER = 'folder'
    IMAGE = 'image'
    PHOTO = 'photo'
    AUDIO = 'audio'
    VIDEO = 'video'
    ALL = [FOLDER, IMAGE, PHOTO, AUDIO, VIDEO, FILE]  # Order matters.


class OneDriveItem:

    def __init__(self, drive, data):
        """
        :param onedrive_d.api.drives.DriveObject drive: The parent drive object.
        :param dict[str, T] data: JSON response for an Item resource.
        """
        self.drive = drive
        self._data = data
        if 'fileSystemInfo' in data:
            self._fs_info = facets.FileSystemInfoFacet(data['fileSystemInfo'])
        else:
            self._fs_info = None

    @property
    def id(self):
        """
        :return str: The unique identifier of the item within the Drive. Read-only.
        """
        return self._data['id']

    @property
    def is_folder(self):
        """
        :return True | False: True if the item is a folder; False if the item is a file (image, audio, ..., inclusive).
        """
        return OneDriveItemTypes.FOLDER in self._data

    @property
    def type(self):
        """
        :return str: The type of the item, represented by a string in OneDriveItemTypes.
        """
        for x in OneDriveItemTypes.ALL:
            if x in self._data:
                return x

    @property
    def name(self):
        """
        :return str: The name of the item (filename and extension). Read-write.
        """
        return self._data['name']

    @name.setter
    def name(self, value):
        """
        :param str value: New name for the item.
        """
        self._data['name'] = value

    @property
    def description(self):
        """
        :return str: Provide a user-visible description of the item. Read-write.
        """
        return self._data['description']

    @description.setter
    def description(self, value):
        """
        :param str value: New description for the item.
        """
        self._data['description'] = value

    @property
    def e_tag(self):
        """
        :return str: eTag for the entire item (metadata + content). Read-only.
        """
        return self._data['eTag']

    @property
    def c_tag(self):
        """
        :return str: An eTag for the content of the item. This eTag is not changed if only the metadata is changed.
        """
        return self._data['cTag']

    @property
    def created_by(self):
        """
        :return onedrive_d.api.identities.IdentitySet: Identity of the user, device, and app which created the item.
        """
        return identities.IdentitySet(self._data['createdBy'])

    @property
    def last_modified_by(self):
        """
        :return onedrive_d.api.identities.IdentitySet: Identity of the user, device, and app which created the item.
        """
        return identities.IdentitySet(self._data['lastModifiedBy'])

    @property
    def size(self):
        """
        :return int: Size of the item in bytes. Read-only.
        """
        return self._data['size']

    @property
    def parent_reference(self):
        """
        :return onedrive_d.api.resources.ItemReferenceResource: Parent information, if the item has a parent.
        """
        return resources.ItemReferenceResource(self._data['parentReference'])

    @property
    def web_url(self):
        """
        :return str: URL that displays the resource in the browser. Read-only.
        """
        return self._data['webUrl']

    @property
    def folder_props(self):
        """
        :return onedrive_d.api.facets.FolderFacet: Folder metadata, if the item is a folder. Read-only.
        """
        return facets.FolderFacet(self._data['folder'])

    @property
    def children(self):
        if not hasattr(self, '_children'):
            self._children = {d['id']: OneDriveItem(self.drive, d) for d in self._data['children']}
        return self._children

    @property
    def file_props(self):
        """
        :return onedrive_d.api.facets.FileFacet: File metadata, if the item is a file. Read-only.
        """
        return facets.FileFacet(self._data['file'])

    @property
    def image_props(self):
        """
        :return onedrive_d.api.facets.ImageFacet: Image metadata, if the item is an image. Read-only.
        """
        return facets.ImageFacet(self._data['image'])

    @property
    def photo_props(self):
        """
        :return onedrive_d.api.facets.PhotoFacet: Photo metadata, if the item is a photo. Read-only.
        """
        return facets.PhotoFacet(self._data['photo'])

    @property
    def audio_props(self):
        """
        :return onedrive_d.api.facets.AudioFacet: Audio metadata, if the item is an audio file. Read-only.
        """
        # TODO: finish AudioFacet
        raise NotImplementedError("Not implemented yet.")

    @property
    def video_props(self):
        """
        :return onedrive_d.api.facets.VideoFacet: Video metadata, if the item is a video file. Read-only.
        """
        # TODO: finish VideoFacet
        raise NotImplementedError("Not implemented yet.")

    @property
    def location_props(self):
        """
        :return onedrive_d.api.facets.LocationFacet: Location metadata, if the item has location data. Read-only.
        """
        # TODO: finish LocationFacet
        raise NotImplementedError("Not implemented yet.")

    @property
    def deletion_props(self):
        """
        :return onedrive_d.api.facets.DeletedFacet: Information about the deleted state of the item. Read-only.
        """
        # TODO: finish DeletedFacet
        raise NotImplementedError("Not implemented yet.")

    @property
    def fs_info(self):
        """
        :return facets.FileSystemInfoFacet:
        """
        return self._fs_info

    @property
    def created_time(self):
        """
        :return int: A UNIX timestamp representing the time when the item was created. Client timestamp preferred.
        """
        if self._fs_info is not None:
            return self._fs_info.created_time
        return parse_datetime(self._data['createdDateTime'])

    @property
    def modified_time(self):
        """
        :return int: A UNIX timestamp representing the time when the item was last modified. Client timestamp preferred.
        """
        if self._fs_info is not None:
            return self._fs_info.modified_time
        return parse_datetime(self._data['lastModifiedDateTime'])
