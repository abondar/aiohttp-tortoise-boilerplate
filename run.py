import argparse
import asyncio
import logging

import uvloop
from aiohttp import web
from tortoise import Tortoise

import settings
from app.router import setup_routes
from app.services.db_client import DBAsyncClient
from run_migrations import run_migrations
from settings import DB_CONFIG


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def start_app(port):
    app = web.Application()
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)s %(message)s',
        level=settings.LOG_LEVEL
    )

    app['db'] = DBAsyncClient(**DB_CONFIG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app['db'].create_connection())
    Tortoise.init(app['db'])
    loop.run_until_complete(run_migrations())
    setup_routes(app)
    web.run_app(app, port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port where server will be serving')
    args = parser.parse_args()
    port = int(args.port) if args.port else 5000
    start_app(port)
