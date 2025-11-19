"""
Alembic Migration Environment Configuration (Async-Compatible)

This module configures Alembic to work with async SQLAlchemy and PostgreSQL.
It supports both offline (SQL generation) and online (database execution) modes.

The configuration is designed to work with the Hudson Bay Expedition Console's
async database architecture using asyncpg driver.
"""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import models for autogenerate support
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base
import models  # Import all models so alembic can detect them

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support
# This allows Alembic to automatically detect schema changes
target_metadata = Base.metadata

# Get database URL from environment variable (preferred) or config
database_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))

# Ensure async driver is used
if database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Override the URL in config with environment variable
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    This is useful for generating SQL scripts for manual review or
    for databases that don't allow direct connections.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Execute migrations within a connection context.

    Args:
        connection: Active database connection to run migrations on

    This function is called by both sync and async migration runners.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode using async engine.

    In this scenario we need to create an async Engine and associate
    a connection with the context.

    This is the primary method for running migrations against the
    async PostgreSQL database using asyncpg driver.
    """
    # Create async engine from configuration
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool connections for migrations
    )

    # Use async context manager for connection
    async with connectable.connect() as connection:
        # Run migrations in sync context within async connection
        await connection.run_sync(do_run_migrations)

    # Dispose of the engine
    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Entry point for online migrations.

    This wraps the async migration runner to work with Alembic's
    synchronous command-line interface.
    """
    # Run async migrations using asyncio
    asyncio.run(run_async_migrations())


# Determine which mode to run in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
