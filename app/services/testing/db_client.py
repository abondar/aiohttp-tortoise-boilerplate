import asyncpg

from app.services.db_client import DBAsyncClient
from run_migrations import run_migrations


class ConnectionWrapper:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def create_test_database(db_config):
    template = 'postgres://{user}:{password}@{host}:{port}/{database}'
    dsn = template.format(**db_config)
    connection = await asyncpg.connect(dsn)
    await connection.execute(f"CREATE DATABASE {db_config['test_database']} OWNER {db_config['user']}")
    test_dsn = template.format(
        user=db_config['user'],
        password=db_config['password'],
        database='racing_test',
        host=db_config['host'],
        port=db_config['port']
    )
    await run_migrations(test_dsn)


async def drop_test_database(db_config):
    dsn = 'postgres://{user}:{password}@{host}:{port}/{database}'.format(**db_config)
    connection = await asyncpg.connect(dsn)
    await connection.execute(f"DROP DATABASE {db_config['test_database']}")


class DBAsyncTestClient(DBAsyncClient):
    async def _init_db(self):
        self._connection = await asyncpg.connect(self.dsn)

    def acquire_connection(self):
        return ConnectionWrapper(self._connection)

    async def close_connection(self):
        await self._connection.close()
