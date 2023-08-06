from requests import HTTPError

class YextBaseException(Exception):
    pass

class YextException(HTTPError):
    pass

class RequestException(YextException):

    def __init__(self, message, status, codes):
        super(YextException, self).__init__(message)
        self.message = message
        self.status = status
        self.codes = codes
