"""Async SQLAlchemy engine and session factory."""

import uuid
from sqlalchemy import String, TypeDecorator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class GUID(TypeDecorator):
    """Platform-independent UUID type. Uses CHAR(32) on SQLite, native UUID on PostgreSQL."""
    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return value.hex
            return uuid.UUID(value).hex
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value

_db_url = settings.async_database_url
_is_sqlite = _db_url.startswith("sqlite")
_connect_args = {}
if "neon.tech" in _db_url:
    _connect_args = {"ssl": "require"}
elif _is_sqlite:
    _connect_args = {"check_same_thread": False}

_engine_kwargs = dict(echo=False, connect_args=_connect_args)
if not _is_sqlite:
    _engine_kwargs.update(pool_size=20, max_overflow=10)

engine = create_async_engine(_db_url, **_engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    """Dependency that yields an async DB session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables (for dev; use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
