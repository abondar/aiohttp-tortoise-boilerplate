import asyncio
import logging

import asyncpg

from settings import DB_CONFIG


class DBAsyncClient:
    DSN = 'postgres://{user}:{password}@{host}:{port}/{database}'

    def __init__(self):
        self._db_pool = None
        self.log = logging.getLogger()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.ensure_future(self._init_db()))

    async def _init_db(self):
        self._db_pool = await asyncpg.create_pool(self.DSN.format(**DB_CONFIG))
