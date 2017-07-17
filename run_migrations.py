import argparse
import asyncio
import os

import aiopg

from settings import DB_CONFIG

DSN = 'dbname={database} user={user} password={password} host={host} port={port}'

async def run_migrations():
    db_pool = await aiopg.create_pool(DSN.format(**DB_CONFIG))
    migrations = sorted([m for m in os.listdir('app/migrations/') if m.endswith('.sql')])
    first_migration = next((m for m in migrations), None)
    if not first_migration:
        print('Initial migration not found')

    async with db_pool.acquire() as connection:
        async with connection.cursor() as cur:
            await cur.execute(open('app/migrations/{}'.format(first_migration)).read())

        async with connection.cursor() as cur:
            await cur.execute('''INSERT INTO "migrations" (migration_name) VALUES (%s)
                  ON CONFLICT (migration_name) DO NOTHING''', (first_migration, ))

        async with connection.cursor() as cur:
            await cur.execute('''SELECT migration_name FROM migrations''')
            result = await cur.fetchall()
            completed_migrations = {stage[0] for stage in result}

        migrations_for_run = sorted(set(migrations) - completed_migrations)

    async with db_pool.acquire() as connection:
        for migration in migrations_for_run:
            print('Running migration {}'.format(migration))
            async with connection.cursor() as cur:
                await cur.execute(open('app/migrations/{}'.format(migration)).read())

            async with connection.cursor() as cur:
                await cur.execute('INSERT INTO "migrations" (migration_name) VALUES (%s)', (migration, ))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.run_until_complete(asyncio.ensure_future(run_migrations()))
