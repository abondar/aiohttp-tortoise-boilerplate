from aiohttp import web
from collections.abc import MutableMapping, Mapping
from numbers import Integral


class BaseAPIException(Exception):
    default_message = 'Error while processing request'
    default_status_code = 400

    def __init__(self, details=None, status_code=None, *args, **kwargs):
        super().__init__(details, status_code, *args)
        assert not details or isinstance(details, Mapping), 'details should be dict-like object'
        assert not status_code or isinstance(status_code, Integral), 'status_code should be int'
        self.details = details if details else {'details': self.default_message}
        self.status_code = status_code if status_code else self.default_status_code

    @property
    def response(self):
        return web.json_response(self.details, status=self.status_code)


class APIException(BaseAPIException):
    default_error_code = 100

    def __init__(self, details=None, error_code=None, *args, **kwargs):
        super().__init__(details=details, *args, **kwargs)
        assert not error_code or isinstance(error_code, Integral), 'error_code should be int'
        self.details['errorCode'] = error_code if error_code else self.default_error_code


class ProcessingError(APIException):
    def __init__(self, message=None, *args, **kwargs):
        assert not message or isinstance(message, str), 'message should be string'
        details = {'details': message if message else self.default_message}
        super().__init__(details=details, *args, **kwargs)


class NotFound(ProcessingError):
    default_message = 'Object not found'
    default_status_code = 404
    default_error_code = 404


class AuthError(ProcessingError):
    default_message = 'Auth failed'
    default_error_code = 401
    default_status_code = 401

