class OneDriveError(Exception):
    def __init__(self, bad_request):
        super().__init__()
        try:
            error_with_description = bad_request.json()
        except ValueError as e:
            self.__class__ = OneDriveInvaildRepsonseFormat
            self.build_error_description(bad_request)
            return
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
            self.__class__ = OneDriveInvaildRepsonseFormat
            self.build_error_description(bad_request)
            return
        if self.errno == 'unauthenticated':
            self.__class__ = OneDriveUnauthorizedError

    def __str__(self):
        return self.strerror + ' (' + self.errno + ')'

    def build_error_description(self, bad_request):
        self.errno = 'url:' + bad_request.url + ' ' + str(bad_request.headers) + ' ' + bad_request.text
        self.strerror = 'status code:' + str(bad_request.status_code)

class OneDriveTokenExpiredError(OneDriveError):
    pass

class OneDriveServerInternalError(OneDriveError):
    pass

class OneDriveUnauthorizedError(OneDriveError):
    pass

class OneDriveInvaildRepsonseFormat(OneDriveError):
    pass

class OneDriveRecoverableError(Exception):
    def __init__(self, retry_after_seconds):
        super().__init__()
        self.retry_after_seconds = retry_after_seconds
