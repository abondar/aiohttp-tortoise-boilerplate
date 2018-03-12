import asyncio
import logging

from pypika import PostgreSQLQuery as Query, JoinType
from pypika import Table, Order
from pypika.functions import Count

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

    def in_transaction(self):
        if self.single_connection:
            return TransactionWrapper(connection=self._connection)
        else:
            return TransactionWrapper(pool=self._db_pool)

    async def _generic_get_data(self, table_name, fields, params_info, **kwargs):
        table = Table(table_name)
        query = Query.from_(table).select(*[getattr(table, field) for field in fields])
        for key, value in kwargs.items():
            if key in params_info:
                param = params_info[key]
                query = query.where(param['operator'](getattr(table, param['field']), value))
        if 'limit' in kwargs:
            query = query.limit(kwargs.get('limit'))
        if 'offset' in kwargs:
            query = query.offset(kwargs.get('offset'))
        async with self.acquire_connection() as connection:
            self.log.debug(query)
            results = await connection.fetch(str(query))
            return [dict(**entry) for entry in results]

    async def _generic_get_count(self, table_name, params_info, **kwargs):
        table = Table(table_name)
        query = Query.from_(table).select(Count(table.star))
        for key, value in kwargs.items():
            if key in params_info:
                param = params_info[key]
                query = query.where(param['operator'](getattr(table, param['field']), value))
        async with self.acquire_connection() as connection:
            self.log.debug(query)
            count = await connection.fetchval(str(query))
            return count

    async def _select_related_data(self, objects, table_name):
        related_objects_for_fetch = set()
        for instance in objects:
            related_objects_for_fetch.add(getattr(instance, f'{table_name}_id'))
        if related_objects_for_fetch:
            method = getattr(self, f'get_{table_name}_list')
            related_object_list = await method(id__in=list(related_objects_for_fetch))
            related_object_map = {a.id: a for a in related_object_list}
            for instance in objects:
                setattr(instance, table_name, related_object_map.get(getattr(instance, f'{table_name}_id')))
        return objects


class TransactionWrapper(DBAsyncClient):
    def __init__(self, pool=None, connection=None):
        assert bool(pool) != bool(connection), 'You must pass either connection or pool'
        self._connection = connection
        self.log = logging.getLogger()
        self._pool = pool
        self.single_connection = True

    def acquire_connection(self):
        return ConnectionWrapper(self._connection)

    async def _get_connection(self):
        return await self._pool._acquire(None)

    async def __aenter__(self):
        if not self._connection:
            self._connection = await self._get_connection()
        self.transaction = self._connection.transaction()
        await self.transaction.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.transaction.rollback()
            return False
        await self.transaction.commit()
        if self._pool:
            await self._pool.release(self._connection)
