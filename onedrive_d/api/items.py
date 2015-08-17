from onedrive_d import str_to_datetime
from onedrive_d.api import resources
from onedrive_d.api import facets


class OneDriveItemTypes:
    FILE = 'file'
    FOLDER = 'folder'
    IMAGE = 'image'
    PHOTO = 'photo'
    AUDIO = 'audio'
    VIDEO = 'video'
    ALL = [FOLDER, IMAGE, PHOTO, AUDIO, VIDEO, FILE]  # Order matters.


class ItemCollection:
    def __init__(self, drive, data):
        self._drive = drive
        self._data = data
        self._page_count = 0

    @property
    def has_next(self):
        """
        :return True | False: Whether or not there are more sets to fetch.
        """
        return '@odata.nextLink' in self._data

    def get_next(self):
        """
        :return [onedrive_d.api.items.OneDriveItem]: Assuming there is at least one more set, return a list of
        OneDriveItems.
        """
        if self._page_count > 0:
            request = self._drive.root.account.session.get(self._data['@odata.nextLink'])
            self._data = request.json()
        self._page_count += 1
        return [OneDriveItem(self._drive, d) for d in self._data['value']]


class OneDriveItem:
    def __init__(self, drive, data):
        """
        :param onedrive_d.api.drives.DriveObject drive: The parent drive object.
        :param dict[str, str | int | dict[str, str | int | dict]] data: JSON response for an Item resource.
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
        :rtype: str
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
        :rtype: str
        """
        for x in OneDriveItemTypes.ALL:
            if x in self._data:
                return x

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._data['name']

    @property
    def description(self):
        """
        :rtype: str
        """
        return self._data['description']

    @property
    def e_tag(self):
        """
        :rtype: str
        """
        return self._data['eTag'] if 'eTag' in self._data else None

    @property
    def c_tag(self):
        """
        :rtype: str
        """
        return self._data['cTag'] if 'eTag' in self._data else None

    @property
    def created_by(self):
        """
        :rtype: resources.IdentitySet
        """
        return resources.IdentitySet(self._data['createdBy'])

    @property
    def last_modified_by(self):
        """
        :rtype: resources.IdentitySet
        """
        return resources.IdentitySet(self._data['lastModifiedBy'])

    @property
    def size(self):
        """
        :rtype: int
        """
        return self._data['size']

    def _get_prop(self, prop, key, type):
        if not hasattr(self, prop):
            setattr(self, prop, type(self._data[key]))
        return getattr(self, prop)

    @property
    def parent_reference(self):
        """
        :rtype: onedrive_d.api.resources.ItemReference
        """
        return self._get_prop('_parent_reference', 'parentReference', resources.ItemReference)

    @property
    def web_url(self):
        """
        :rtype: str
        """
        return self._data['webUrl']

    @property
    def folder_props(self):
        """
        :rtype: onedrive_d.api.facets.FolderFacet
        """
        return self._get_prop('_folder_props', 'folder', facets.FolderFacet)

    @property
    def children(self):
        if not hasattr(self, '_children'):
            # noinspection PyAttributeOutsideInit
            self._children = {d['id']: OneDriveItem(self.drive, d) for d in self._data['children']}
        return self._children

    @property
    def file_props(self):
        """
        :rtype: onedrive_d.api.facets.FileFacet
        """
        return self._get_prop('_file_props', 'file', facets.FileFacet)

    @property
    def image_props(self):
        """
        :rtype: onedrive_d.api.facets.ImageFacet
        """
        return self._get_prop('_image_props', 'image', facets.ImageFacet)

    @property
    def photo_props(self):
        """
        :rtype: onedrive_d.api.facets.PhotoFacet
        """
        return self._get_prop('_photo_props', 'photo', facets.PhotoFacet)

    @property
    def audio_props(self):
        """
        :rtype: onedrive_d.api.facets.AudioFacet
        """
        return self._get_prop('_audio_props', 'audio', facets.AudioFacet)

    @property
    def video_props(self):
        """
        :rtype: onedrive_d.api.facets.VideoFacet
        """
        return self._get_prop('_video_props', 'video', facets.VideoFacet)

    @property
    def location_props(self):
        """
        :rtype: onedrive_d.api.facets.LocationFacet
        """
        return self._get_prop('_location_props', 'location', facets.LocationFacet)

    @property
    def deleted_props(self):
        """
        :rtype: onedrive_d.api.facets.DeletedFacet
        """
        return self._get_prop('_deleted_props', 'deleted', facets.DeletedFacet)

    @property
    def special_folder_props(self):
        """
        :rtype: onedrive_d.api.facets.DeletedFacet
        """
        return self._get_prop('_special_folder_props', 'specialFolder', facets.SpecialFolderFacet)

    @property
    def fs_info(self):
        """
        :return facets.FileSystemInfoFacet:
        """
        return self._fs_info

    @property
    def created_time(self):
        """
        :rtype: int
        """
        if self._fs_info is not None:
            return self._fs_info.created_time
        return str_to_datetime(self._data['createdDateTime'])

    @property
    def modified_time(self):
        """
        :rtype: int
        """
        if self._fs_info is not None:
            return self._fs_info.modified_time
        return str_to_datetime(self._data['lastModifiedDateTime'])
