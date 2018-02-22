import argparse
import asyncio
import logging

from aiohttp import web

import settings
from app.router import setup_routes
from app.services.db_client import DBAsyncClient
from run_migrations import run_migrations
from settings import DB_CONFIG


def start_app(port):
    app = web.Application()
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        level=settings.LOG_LEVEL
    )

    app['db'] = DBAsyncClient(**DB_CONFIG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_migrations())
    setup_routes(app)
    web.run_app(app, port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port, on which server will be serving')
    args = parser.parse_args()
    port = int(args.port) if args.port else 5000
    start_app(port)
