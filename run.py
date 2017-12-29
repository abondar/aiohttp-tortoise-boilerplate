import argparse
import asyncio
import logging

from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient

import settings
from app.router import setup_routes
from run_migrations import run_migrations


async def authenticate(config, db):
    result = None
    if 'password' in config and 'user' in config:
        if 'auth_db' in config:
            result = await db.authenticate(config['user'], config['password'], source=config['auth_db'])
        else:
            result = await db.authenticate(config['user'], config['password'])
    return result


def start_app(port):
    app = web.Application()
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    mongo_client = AsyncIOMotorClient('{}:{}'.format(settings.MONGO_CONFIG['host'], settings.MONGO_CONFIG['port']))
    db = mongo_client[settings.MONGO_CONFIG['db']]
    loop.run_until_complete(asyncio.ensure_future(authenticate(settings.MONGO_CONFIG, db)))

    app['mongo'] = db
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
