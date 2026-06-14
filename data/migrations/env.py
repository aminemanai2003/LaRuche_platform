"""Alembic env.py — async SQLAlchemy + asyncpg."""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context

# Import all models so Alembic can detect them
from db.models import Base  # noqa: F401  # type: ignore[import]
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url.replace("postgres://", "postgresql+asyncpg://").replace(
            "postgresql://", "postgresql+asyncpg://"
        )
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "wealthmesh")
    user = os.getenv("POSTGRES_USER", "wealthmesh")
    pw = os.getenv("POSTGRES_PASSWORD", "changeme")
    return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    context.configure(
        url=_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: object) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)  # type: ignore[arg-type]
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = _db_url()
    connectable = async_engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
