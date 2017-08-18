import asyncio
import os

import asyncpg

from settings import DB_CONFIG


DSN = 'postgres://{user}:{password}@{host}:{port}/{database}'

async def run_migrations():
    db_pool = await asyncpg.create_pool(DSN.format(**DB_CONFIG))
    migrations = sorted([m for m in os.listdir('app/migrations/') if m.endswith('.sql')])
    first_migration = next((m for m in migrations), None)
    if not first_migration:
        print('Initial migration not found')

    async with db_pool.acquire() as connection:
        await connection.execute(open('app/migrations/{}'.format(first_migration)).read())

        await connection.execute('''INSERT INTO migration (migration_name) VALUES ($1)
              ON CONFLICT (migration_name) DO NOTHING''', first_migration,)

        result = await connection.fetch('''SELECT migration_name FROM migration''')
        completed_migrations = {stage['migration_name'] for stage in result}

        migrations_for_run = sorted(set(migrations) - completed_migrations)

        for migration in migrations_for_run:
            print('Running migration {}'.format(migration))
            async with connection.transaction():
                await connection.execute(open('app/migrations/{}'.format(migration)).read())
                await connection.execute('INSERT INTO migration (migration_name) VALUES ($1)', migration)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.run_until_complete(asyncio.ensure_future(run_migrations()))
