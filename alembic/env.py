import os
from logging.config import fileConfig

from alembic import context
from alembic.config import Config
from sqlalchemy import engine_from_config, pool

from dotenv import load_dotenv

load_dotenv()

config: Config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.db.base import Base
from app.db.session import get_settings
from app import models

settings = get_settings()
sync_url = settings.database_url.replace("asyncpg", "psycopg2")
config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
