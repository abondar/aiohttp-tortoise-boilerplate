import asyncio
import os

import asyncpg

from settings import DB_CONFIG


DSN = 'postgres://{user}:{password}@{host}:{port}/{database}'

async def run_migrations(dsn=None):
    if not dsn:
        dsn = DSN.format(**DB_CONFIG)
    connection = await asyncpg.connect(dsn)
    migrations = sorted([m for m in os.listdir('migrations/') if m.endswith('.sql')])
    first_migration = next((m for m in migrations), None)
    if not first_migration:
        logging.error('Initial migration not found')
        return

    with open('migrations/{}'.format(first_migration)) as migration_file:
        await connection.execute(migration_file.read())

    result = await connection.fetch('''SELECT migration_name FROM migration''')
    completed_migrations = {stage['migration_name'] for stage in result}

    migrations_for_run = sorted(set(migrations) - completed_migrations)

    for migration in migrations_for_run:
        logging.info('Running migration {}'.format(migration))
        async with connection.transaction():
            with open('migrations/{}'.format(migration)) as migration_file:
                await connection.execute(migration_file.read())
            await connection.execute('INSERT INTO migration (migration_name) VALUES ($1)', migration)
    await connection.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(run_migrations()))
