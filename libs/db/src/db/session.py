"""Async SQLAlchemy session factory."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.models import Base

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        # Convert postgres:// → postgresql+asyncpg://
        return url.replace("postgres://", "postgresql+asyncpg://").replace(
            "postgresql://", "postgresql+asyncpg://"
        )
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "wealthmesh")
    user = os.getenv("POSTGRES_USER", "wealthmesh")
    pw = os.getenv("POSTGRES_PASSWORD", "changeme")
    return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{db}"


def init_db(url: str | None = None) -> None:
    global _engine, _session_factory
    _engine = create_async_engine(url or _db_url(), echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        init_db()
    assert _session_factory is not None
    async with _session_factory() as session:
        yield session


async def create_tables(url: str | None = None) -> None:
    """Create all tables (dev/test only — use Alembic in production)."""
    if _engine is None:
        init_db(url)
    assert _engine is not None
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
