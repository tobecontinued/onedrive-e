class OneDriveError(Exception):
    def __init__(self, error_with_description):
        super().__init__()
        if 'error_description' in error_with_description:
            self.errno = error_with_description['error']
            self.strerror = error_with_description['error_description']
        elif 'error' in error_with_description:
            self.errno = error_with_description['error']['code']
            self.strerror = error_with_description['error']['message']
            if self.errno == 'request_token_expired':
                self.__class__ = OneDriveTokenExpiredError
            elif self.errno == 'server_internal_error':
                self.__class__ = OneDriveServerInternalError
        else:
            raise ValueError('Unknown OneDrive error format - ' + str(error_with_description))

    def __str__(self):
        return self.strerror + ' (' + self.errno + ')'


class OneDriveTokenExpiredError(OneDriveError):
    pass


class OneDriveServerInternalError(OneDriveError):
    pass


class OneDriveRecoverableError(Exception):
    def __init__(self, retry_after_seconds):
        super().__init__()
        self.retry_after_seconds = retry_after_seconds
