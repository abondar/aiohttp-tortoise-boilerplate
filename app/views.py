import asyncio

from aiohttp import web, hdrs
from marshmallow import Schema

from app.exceptions import APIException


class BaseView(web.View):
    serializer = Schema()

    async def pre_process_request(self):
        if self.request._method in {hdrs.METH_POST, hdrs.METH_PUT, hdrs.METH_PATCH, hdrs.METH_DELETE}:
            data = await self.request.json()
        else:
            data = self.request.query
        result = self.serializer.load(data)
        if result.errors:
            raise APIException(result.errors, 400)
        self.validated_data = result.data

    @asyncio.coroutine
    def __iter__(self):
        if self.request._method not in hdrs.METH_ALL:
            self._raise_allowed_methods()
        method = getattr(self, self.request._method.lower(), None)
        if method is None:
            self._raise_allowed_methods()
        try:
            yield from self.pre_process_request()
            resp = yield from method()
        except APIException as e:
            return e.response
        return resp
