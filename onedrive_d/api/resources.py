from ciso8601 import parse_datetime


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


class AsyncCopySession:
    """
    Track the state of an async copy request.
    """

    def __init__(self, drive, headers):
        self.drive = drive
        self.url = headers['Location']
