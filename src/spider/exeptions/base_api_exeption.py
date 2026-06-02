from rest_framework.exceptions import APIException


class BaseApiException(APIException):
    detail = None
    status_code = None

    def __init__(self, status_code, message) -> None:
        # override public fields
        self.status_code = status_code
        self.detail = message
