import argparse

import aiopg
import yaml
from aiohttp import web, asyncio
from app.router import setup_routes
from run_migrations import run_migrations

DSN = 'dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}'


async def db_middleware(app, handler):
    async def middleware(request):
        if request.match_info.route.name:
            if not app.get('db'):
                app['db'] = await aiopg.create_pool(app['db_dsn'])
            request['db'] = app['db']
        return await handler(request)
    return middleware


def start_app(port):
    app = web.Application(middlewares=[db_middleware])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(run_migrations()))
    setup_routes(app)
    web.run_app(app, port=port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port, on which server will be serving')
    args = parser.parse_args()
    port = int(args.port) if args.port else 80
    start_app(port)
