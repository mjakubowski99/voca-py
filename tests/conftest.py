from typing import AsyncIterator
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from config import settings
from src.main import app
from src.entry.models import Base

TEST_DB_URL = settings.database_url


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"

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
async def setup_database(test_engine) -> AsyncIterator[None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
    ) as client:
        yield client
