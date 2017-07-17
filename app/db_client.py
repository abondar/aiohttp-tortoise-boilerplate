import logging

import asyncio

import aiopg

from settings import DB_CONFIG


class DBClient:
    DSN = 'dbname={database} user={user} password={password} host={host} port={port}'

    def __init__(self):
        self._db_pool = None
        self.log = logging.getLogger()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.ensure_future(self._init_db()))

    async def _init_db(self):
        self._db_pool = await aiopg.create_pool(self.DSN.format(**DB_CONFIG))
