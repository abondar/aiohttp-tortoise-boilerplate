import argparse

import aiopg
import yaml
from aiohttp import web
from app.router import setup_routes

DSN = 'dbname={db_name} user={db_user} password={db_password} host={db_host} port={db_port}'


async def db_middleware(app, handler):
    async def middleware(request):
        if request.match_info.route.name:
            if not app.get('db'):
                app['db'] = await aiopg.create_pool(app['db_dsn'])
            request['db'] = app['db']
        return await handler(request)
    return middleware

async def app_middleware(app, handler):
    async def middleware(request):
        request['app'] = app
        return await handler(request)
    return middleware


def start_app(port):
    app = web.Application(middlewares=[db_middleware, app_middleware])
    with open("config/topline.yaml", 'r') as stream:
        config = yaml.load(stream)
        app['db_dsn'] = DSN.format(**config)
    setup_routes(app)
    web.run_app(app, port=port)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Port, on which server will be serving')
    args = parser.parse_args()
    port = int(args.port) if args.port else 80
    start_app(port)
