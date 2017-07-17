import asyncio

from aiohttp import web


class IndexView(web.View):
    async def get(self):
        return web.json_response({'result': 'success!'})

