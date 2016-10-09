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
            raise OneDriveInvaildRepsonseFormat()

    def __str__(self):
        return self.strerror + ' (' + self.errno + ')'


class OneDriveTokenExpiredError(OneDriveError):
    pass


class OneDriveServerInternalError(OneDriveError):
    pass

class OneDriveInvaildRepsonseFormat(OneDriveError):
    def __init__(self, bad_request= None):
        if bad_request is not None :
            error_msg = 'url:' + bad_request.url + ' ' + str(bad_request.headers) + ' ' + bad_request.text
            error_with_description = {'error' : error_msg, 
            'error_description' : 'status code:' + str(bad_request.status_code)}
        else:
            error_with_description = {'error' : 'Unknown Error', 
            'error_description' : 'Invaild Repsonse Format'}
        super().__init__(error_with_description)

class OneDriveRecoverableError(Exception):
    def __init__(self, retry_after_seconds):
        super().__init__()
        self.retry_after_seconds = retry_after_seconds
