__author__ = 'xb'

import json

from onedrive_d import str_to_datetime
from onedrive_d.api import options


class UserProfile:
    VERSION_KEY = '@version'
    VERSION_VALUE = 1

    def __init__(self, data):
        self._data = data

    @property
    def user_id(self):
        """
        :rtype: str
        """
        return self._data['id']

    @property
    def gender(self):
        """
        :rtype: str | None
        """
        return self._data['gender']

    @property
    def locale(self):
        """
        :rtype: str
        """
        return self._data['locale']

    @property
    def first_name(self):
        """
        :rtype: str
        """
        return self._data['first_name']

    @property
    def last_name(self):
        """
        :rtype: str
        """
        return self._data['last_name']

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._data['name']

    def dump(self):
        return json.dumps({'data': self._data, self.VERSION_KEY: self.VERSION_VALUE})

    @classmethod
    def load(cls, s):
        """
        :param str s: Some value previously returned by dump() call.
        :rtype: onedrive_d.api.resources.UserProfile
        """
        data = json.loads(s)
        if cls.VERSION_KEY not in data:
            raise ValueError('Unsupported user profile serialization data.')
        if data[cls.VERSION_KEY] != cls.VERSION_VALUE:
            raise ValueError('Outdated user profile serialization.')
        return UserProfile(data['data'])


class ItemReference:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/resources/itemReference.md
    """

    def __init__(self, data):
        """
        :param dict[str, str] data: Deserialized JSON dict of ItemReference resource.
        """
        self.data = data

    @property
    def drive_id(self):
        """
        Unique identifier for the Drive that contains the item.
        :rtype: str
        """
        return self.data['driveId']

    @property
    def id(self):
        """
        Unique identifier for the item.
        :rtype: str
        """
        return self.data['id']

    @property
    def path(self):
        """
        Path that used to navigate to the item.
        :rtype: str
        """
        return self.data['path']

    @classmethod
    def build(cls, drive_id=None, id=None, path=None):
        """
        Build a ItemReference object from parameters.
        :param str | None drive_id: (Optional) ID of the root drive.
        :param str | None id: (Optional) ID of the item.
        :param str | None path: (Optional) Path to the item relative to drive root.
        :rtype: ItemReference
        """
        if id is None and path is None:
            raise ValueError('id and path cannot be both None.')
        data = {}
        if drive_id is not None:
            data['driveId'] = drive_id
        if id is not None:
            data['id'] = id
        if path is not None:
            data['path'] = path
        return ItemReference(data)


class UploadSession:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/resources/uploadSession.md
    """

    def __init__(self, data):
        self.update(data)

    # noinspection PyAttributeOutsideInit
    def update(self, data):
        if 'uploadUrl' in data:
            self.upload_url = data['uploadUrl']
        if 'expirationDateTime' in data:
            self.expires_at = str_to_datetime(data['expirationDateTime'])
        self.next_ranges = []
        if 'nextExpectedRanges' in data:
            for s in data['nextExpectedRanges']:
                f, t = s.split('-', 1)
                f = int(f)
                if t == '':
                    t = None
                else:
                    t = int(t)
                self.next_ranges.append((f, t))


class AsyncCopySession:
    """
    Track the state of an async copy request.
    """
    ACCEPTABLE_STATUS_CODES = {200, 202, 303}

    def __init__(self, drive, headers):
        self.drive = drive
        self.url = headers['Location']
        self._status = options.AsyncOperationStatuses.NOT_STARTED

    def update_status(self):
        request = self.drive.root.account.session.get(self.url, ok_status_code=self.ACCEPTABLE_STATUS_CODES)
        if request.status_code == 202:
            data = request.json()
            self._operation = data['operation']
            self._percentage_complete = data['percentageComplete']
            self._status = data['status']
        elif request.status_code == 200:
            self._percentage_complete = 100
            self._status = options.AsyncOperationStatuses.COMPLETED
            self._item = self.drive.build_item(request.json())

    @property
    def operation(self):
        """
        :return str: The type of job being run.
        """
        return self._operation

    @property
    def percentage_complete(self):
        """
        :return float: An float value between 0 and 100 that indicates the percentage complete.
        """
        return self._percentage_complete

    @property
    def status(self):
        """
        :return str: An enum value in options.AsyncOperationStatuses to indicate the status of the job.
        """
        return self._status

    def get_item(self):
        return self._item

class Identity:
    def __init__(self, data):
        self._data = data

    @property
    def id(self):
        """
        :rtype: str
        """
        return self._data['id']

    @property
    def display_name(self):
        """
        :rtype: str
        """
        return self._data['displayName']


class IdentitySet:
    """
    Python representations of identity types.
    https://github.com/OneDrive/onedrive-api-docs/blob/master/resources/identitySet.md
    """

    ALL_IDENTITIES = ['user', 'application', 'device']

    def __init__(self, data):
        self._data = {}
        for i in self.ALL_IDENTITIES:
            if i in data:
                self._data[i] = Identity(data[i])
            else:
                self._data[i] = None

    @property
    def user(self):
        """
        An Identity resource that represents a user.
        :rtype: Identity
        """
        return self._data['user']

    @property
    def application(self):
        """
        An Identity resource that represents the application.
        :rtype: Identity
        """
        return self._data['application']

    @property
    def device(self):
        """
        An Identity resource that represents the device.
        :rtype: Identity
        """
        return self._data['device']
