import asyncio
import logging

import asyncpg


def is_in(field, value):
    """
    Wrapper for PyPika isin, to pass it as function operator
    """
    return field.isin(value)


class ConnectionWrapper:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class DBAsyncClient:
    DSN_TEMPLATE = 'postgres://{user}:{password}@{host}:{port}/{database}'

    def __init__(self, user, password, database, host, port, single_connection=False, *args, **kwargs):
        self.dsn = self.DSN_TEMPLATE.format(user=user, password=password, host=host, port=port, database=database)
        self._db_user = user
        self._db_pool = None
        self.log = logging.getLogger()
        self.single_connection = single_connection
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._init_db())

    async def _init_db(self):
        if not self.single_connection:
            self._db_pool = await asyncpg.create_pool(self.dsn)
        else:
            self._connection = await asyncpg.connect(self.dsn)

    def acquire_connection(self):
        if not self.single_connection:
            return self._db_pool.acquire()
        else:
            return ConnectionWrapper(self._connection)
