CREATE TABLE IF NOT EXISTS migrations
(
    id SERIAL PRIMARY KEY NOT NULL,
    migration_name VARCHAR(255) NOT NULL UNIQUE
);