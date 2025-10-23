import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.main import app
from httpx._transports.asgi import ASGITransport
from src.entry.models import Base
from config import settings
from sqlalchemy import text

# Use a separate test database URL
TEST_DATABASE_URL = settings.database_url

@pytest.fixture(scope="session")
def event_loop():
    """Reuse the same event loop for async tests."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def clean_tables(db_session):
    """
    Truncate all tables before each test.
    """
    async with db_session.begin():
        for table in reversed(Base.metadata.sorted_tables):
            await db_session.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE;'))
    yield


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Create all tables in the test database before tests.
    """
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client():
    """
    AsyncClient for testing FastAPI endpoints using ASGITransport.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
