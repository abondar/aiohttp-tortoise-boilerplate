from asyncio import get_event_loop

import pytest
from aiohttp import web
from asyncpg import InvalidCatalogNameError
from tortoise import Tortoise

import settings
from app.router import setup_routes
from app.services.db_client import DBAsyncClient
from app import models
from run_migrations import run_migrations


@pytest.fixture(scope='session')
def tortoise():
    loop = get_event_loop()
    db_config = settings.DB_CONFIG
    db_config['database'] = db_config['database'] + '_test'
    db = DBAsyncClient(single_connection=True, **db_config)
    Tortoise.init(db)
    try:
        loop.run_until_complete(db.execute_db_script(
            f'DROP DATABASE {db_config["database"]}'
        ))
    except InvalidCatalogNameError:
        pass
    loop.run_until_complete(db.execute_db_script(
        f'CREATE DATABASE {db_config["database"]} OWNER {db_config["user"]}'
    ))
    loop.run_until_complete(db.create_connection())
    loop.run_until_complete(run_migrations(db_config=db_config))
    return db


@pytest.fixture
async def app(loop, tortoise, request):
    app = web.Application()
    setup_routes(app)
    app['db'] = tortoise
    await tortoise.create_connection()

    transaction = tortoise.in_transaction()
    await transaction.start()
    Tortoise._set_global_connection(transaction)

    def fin():
        loop.run_until_complete(transaction.rollback())
        loop.run_until_complete(tortoise.close())

    request.addfinalizer(fin)
    return app


@pytest.fixture
async def client(app, aiohttp_client):
    client = await aiohttp_client(app)
    return client
