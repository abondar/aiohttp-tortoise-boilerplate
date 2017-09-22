import argparse

from aiohttp import web, asyncio

from app.router import setup_routes
from app.services.db_client import DBAsyncClient
from run_migrations import run_migrations
from settings import DB_CONFIG


def start_app(port):
    app = web.Application()

    app['db'] = DBAsyncClient(**DB_CONFIG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_migrations())
    setup_routes(app)
    web.run_app(app, port=port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port, on which server will be serving')
    args = parser.parse_args()
    port = int(args.port) if args.port else 80
    start_app(port)
