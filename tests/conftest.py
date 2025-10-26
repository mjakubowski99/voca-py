from typing import AsyncIterator
import uuid
from core.db import get_session, init_db, close_db, set_db_session_context
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import text
from config import settings
from src.main import app
from core.models import Base

TEST_DB_URL = settings.database_url


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


# Separate engine to seed data for test
@pytest.fixture
def test_engine() -> AsyncEngine:
    return create_async_engine(TEST_DB_URL, echo=True)


@pytest.fixture
def async_session_maker(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture
async def session(async_session_maker) -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
async def refresh_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_engine.begin() as conn:
        table_names = ", ".join(
            [
                f'"{table.schema}"."{table.name}"' if table.schema else f'"{table.name}"'
                for table in Base.metadata.sorted_tables
            ]
        )

        if table_names:
            await conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE;"))

    yield


# Fixture to init application database
@pytest.fixture(autouse=True)
async def init_database():
    set_db_session_context(uuid.uuid4())
    await init_db()
    yield
    await get_session().close()
    await close_db()


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
    ) as client:
        yield client
