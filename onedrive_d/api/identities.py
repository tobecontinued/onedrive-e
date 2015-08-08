"""
Python representations of identity types.
https://github.com/OneDrive/onedrive-api-docs/blob/master/resources/identitySet.md
"""


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
