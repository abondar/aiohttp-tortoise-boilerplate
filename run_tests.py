import asyncio
import unittest

from aiohttp import web
from aiohttp.test_utils import TestClient

from app.router import setup_routes
from app.services.testing.db_client import DBAsyncTestClient, create_test_database, drop_test_database
from settings import DB_CONFIG


class AioHttpTestCase(unittest.TestCase):
    @classmethod
    def get_application(cls):
        app = web.Application()

        app['db'] = DBAsyncTestClient(
            user=DB_CONFIG.get('user'),
            password=DB_CONFIG.get('password'),
            database=DB_CONFIG.get('test_database'),
            host=DB_CONFIG.get('host'),
            port=DB_CONFIG.get('port')
        )
        setup_routes(app)
        return app

    async def _get_client(self, app):
        return TestClient(self.app, loop=self.loop)

    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()
        cls.loop.run_until_complete(create_test_database(DB_CONFIG))
        cls.app = cls.get_application()

    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(cls.app['db'].close_connection())
        cls.loop.run_until_complete(drop_test_database(DB_CONFIG))

    async def start_transaction(self):
        async with self.app['db'].acquire_connection() as connection:
            self.transaction = connection.transaction()
        await self.transaction.start()

    def setUp(self):
        self.client = self.loop.run_until_complete(self._get_client(self.app))

        self.loop.run_until_complete(self.client.start_server())
        self.loop.run_until_complete(self.start_transaction())

    def tearDown(self):
        self.loop.run_until_complete(self.transaction.rollback())
        self.loop.run_until_complete(self.client.close())

    # Template for tests:
    #
    # @unittest_run_loop
    # async def test_bet(self):
    #     data = {}
    #     result = await self.client.post('/method', json=data)
    #     response = await result.json()
    #     self.assertEqual(result.status, 200)


if __name__ == '__main__':
    unittest.main()

