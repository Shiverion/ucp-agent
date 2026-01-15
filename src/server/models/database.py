"""Database configuration and session management for UCP server."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DB_PATH", "./data/ucp_custom.db")

# Async engine for FastAPI
async_engine = create_async_engine(
    f"sqlite+aiosqlite:///{DATABASE_URL}",
    echo=False,
)

# Sync engine for scripts
sync_engine = create_engine(
    f"sqlite:///{DATABASE_URL}",
    echo=False,
)


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
sync_session_maker = sessionmaker(sync_engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize the database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_db_sync() -> None:
    """Initialize the database tables synchronously."""
    Base.metadata.create_all(sync_engine)
