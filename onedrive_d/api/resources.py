class ItemReferenceResource:
    """
    https://github.com/OneDrive/onedrive-api-docs/blob/master/resources/itemReference.md
    """

    def __init__(self, data):
        """
        :param dict[str, str] data: Deserialized JSON dict of ItemReference resource.
        """
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

    @id.setter
    def id(self, value):
        """
        :param str value: The string to change ID to.
        """
        self._data['id'] = value

    @property
    def path(self):
        """
        Path that used to navigate to the item.
        :rtype: str
        """
        return self._data['path']

    @path.setter
    def path(self, value):
        """
        :param str value: The string to change path to.
        """
        self._data['path'] = value
