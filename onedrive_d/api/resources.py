from ciso8601 import parse_datetime


class ItemReference:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/resources/itemReference.md
    """

    def __init__(self, data=None, drive_id=None, id=None, path=None):
        """
        :param dict[str, str] data: Deserialized JSON dict of ItemReference resource.
        """
        if data is None:
            data = {}
            if drive_id is not None:
                data['driveId'] = drive_id
            if id is not None:
                data['id'] = id
            if path is not None:
                data['path'] = path
        self._data = data

    @property
    def drive_id(self):
        """
        Unique identifier for the Drive that contains the item.
        :rtype: str
        """
        return self._data['driveId']

    @property
    def id(self):
        """
        Unique identifier for the item.
        :rtype: str
        """
        return self._data['id']

    @property
    def path(self):
        """
        Path that used to navigate to the item.
        :rtype: str
        """
        return self._data['path']


class UploadSession:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/resources/uploadSession.md
    """

    def __init__(self, data):
        self.update(data)

    def update(self, data):
        if 'uploadUrl' in data:
            self.upload_url = data['uploadUrl']
        if 'expirationDateTime' in data:
            self.expires_at = parse_datetime(data['expirationDateTime'])
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
