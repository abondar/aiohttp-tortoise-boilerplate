import asyncio
import collections.abc
from aiohttp import web

from app.exceptions import APIException


class BaseView(web.View):
    @asyncio.coroutine
    def __iter__(self):
        try:
            response = yield from super(BaseView, self).__iter__()
        except APIException as e:
            if isinstance(e.message, str):
                message = {'error': e.message}
            elif isinstance(e.message, collections.abc.Mapping) or isinstance(e.message, collections.abc.Sequence):
                message = e.message
            else:
                message = "Can't serialize {} to dict or list".format(type(e.message).__name__)
                raise TypeError(message)
            return web.json_response(message, status=e.status_code)
        return response


class LoginRequiredView(BaseView):
    authentication_class = None

    @asyncio.coroutine
    def __iter__(self):
        authenticated = yield from self.authentication_class(self.request).authenticate()
        if not authenticated:
            return web.json_response({'error': 'invalid credentials provided'}, status=401)
        response = yield from super(LoginRequiredView, self).__iter__()
        return response

