import asyncio
import logging

import asyncpg


class DBAsyncClient:
    DSN_TEMPLATE = 'postgres://{user}:{password}@{host}:{port}/{database}'

    def __init__(self, user, password, database, host, port, *args, **kwargs):
        self.dsn = self.DSN_TEMPLATE.format(user=user, password=password, host=host, port=port, database=database)
        self._db_user = user
        self._db_pool = None
        self.log = logging.getLogger()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.ensure_future(self._init_db()))

    async def _init_db(self):
        self._db_pool = await asyncpg.create_pool(self.dsn)

    def acquire_connection(self):
        return self._db_pool.acquire()
