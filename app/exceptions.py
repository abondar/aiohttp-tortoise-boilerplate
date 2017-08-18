from aiohttp import web
from collections.abc import MutableMapping
from numbers import Integral


class APIException(Exception):
    def __init__(self, details, status_code=400, error_code=100, *args, **kwargs):
        super().__init__(details, status_code, *args)
        assert isinstance(details, MutableMapping), 'details should be dict-like object'
        assert isinstance(status_code, Integral), 'status_code should be int'
        assert isinstance(error_code, Integral), 'error_code should be int'
        self.details = details
        self.status_code = status_code
        self.details['errorCode'] = error_code

    @property
    def response(self):
        return web.json_response(self.details, status=self.status_code)


class ProcessingError(APIException):
    def __init__(self, message, *args, **kwargs):
        assert isinstance(message, str), 'message should be string'
        details = {'details': message}
        super().__init__(details, *args, **kwargs)

