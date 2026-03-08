"""
Integration test fixtures using testcontainers (PostgreSQL).

Provides:
- postgres_url: connection URL for the disposable test container
- engine: SQLAlchemy async engine pointed at the container
- async_db: AsyncSession scoped to the test function (auto-rolled back)
"""
import os

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.database import Base

# Import all models so Base.metadata knows all tables
import app.modules.auth.models  # noqa: F401
import app.modules.cdm.models  # noqa: F401
import app.modules.query.models  # noqa: F401
import app.modules.agent.models  # noqa: F401
import app.modules.dashboard.models  # noqa: F401
import app.modules.audit.models  # noqa: F401
import app.modules.ingestion.models  # noqa: F401


@pytest.fixture(scope="session")
def postgres_container():
    """Start a disposable Postgres container for the entire test session."""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def sync_engine(postgres_container):
    """Create tables once for the session using a sync engine."""
    from sqlalchemy import create_engine

    # Use psycopg2 for the sync setup call (create_all)
    url = postgres_container.get_connection_url()
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def async_engine_url(postgres_container):
    """Return the asyncpg URL for use in async tests."""
    url = postgres_container.get_connection_url()
    # testcontainers returns postgresql+psycopg2 URL, convert to asyncpg
    return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://").replace(
        "postgresql://", "postgresql+asyncpg://"
    )


@pytest.fixture
async def async_db(sync_engine, async_engine_url):
    """
    Provide an AsyncSession for each test.

    Wraps everything in a SAVEPOINT so the DB state can be rolled back
    after each test (no need to drop/recreate tables between tests).
    """
    engine = create_async_engine(async_engine_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.connect() as conn:
        await conn.begin()
        # Use a nested transaction (SAVEPOINT) for rollback isolation
        async with session_factory(bind=conn) as session:
            await conn.begin_nested()
            try:
                yield session
            finally:
                await conn.rollback()

    await engine.dispose()
