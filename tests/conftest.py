import uuid

from rich.table import Table
from core.db import get_session, init_db, close_db, set_db_session_context
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.sql import select, text
from config import settings
from src.main import app
from core.models import Base
from src.shared.util.hash import IHash
from core.container import container
from tests.client import HttpClient
from tests.factory import (
    ExerciseEntryFactory,
    ExerciseFactory,
    FlashcardPollItemFactory,
    SmTwoFlashcardsFactory,
    UnscrambleWordExerciseFactory,
    UserFactory,
    AdminFactory,
    OwnerFactory,
    FlashcardDeckFactory,
    FlashcardFactory,
)
from tests.asserts import *
from rich.console import Console

console = Console(force_terminal=True)

TEST_DB_URL = settings.database_url


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def dump(capsys):
    """Fixture that forces output even with capture enabled."""

    def _dump(value):
        # Temporarily disable capture
        with capsys.disabled():
            console.print()  # Force new line
            console.print(value, style="bold green")

    return _dump


@pytest.fixture(autouse=True)
def dump_db(dump, session):
    """
    Fixture to dump data from a single table using the default dump function.
    Usage:
        await dump_db(session, Flashcards)
    """

    async def _dump_db(model: type, limit: int = 20):
        result = await session.execute(select(model).limit(limit))
        rows = result.scalars().all()

        if not rows:
            dump(f"No data found in {model.__tablename__}")
            return

        table = Table(title=f"Dump of {model.__tablename__}")
        for column in model.__table__.columns:
            table.add_column(column.name, style="cyan", overflow="fold")

        for row in rows:
            table.add_row(*(str(getattr(row, col.name)) for col in model.__table__.columns))

        dump(table)

    return _dump_db


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
async def client(monkeypatch) -> HttpClient:
    """Client with authentication support."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost",
    ) as async_client:
        auth_client = HttpClient(async_client, monkeypatch)
        yield auth_client
        # Cleanup
        app.dependency_overrides.clear()


@pytest.fixture
def hasher() -> IHash:
    """Fixture zwracająca implementację interfejsu IHash."""
    return container.resolve(IHash)


@pytest.fixture
def user_factory(session, hasher) -> UserFactory:
    return UserFactory(session, hasher)


@pytest.fixture
def admin_factory(session, hasher) -> AdminFactory:
    return AdminFactory(session, hasher)


@pytest.fixture
def owner_factory(user_factory, admin_factory) -> OwnerFactory:
    return OwnerFactory(user_factory, admin_factory)


@pytest.fixture
def deck_factory(session) -> FlashcardDeckFactory:
    return FlashcardDeckFactory(session)


@pytest.fixture
def flashcard_factory(session) -> FlashcardFactory:
    return FlashcardFactory(session)


@pytest.fixture
def sm_two_factory(session) -> SmTwoFlashcardsFactory:
    return SmTwoFlashcardsFactory(session)


@pytest.fixture
def flashcard_poll_factory(session) -> FlashcardPollItemFactory:
    return FlashcardPollItemFactory(session)


@pytest.fixture
def exercise_factory(session) -> ExerciseFactory:
    return ExerciseFactory(session)


@pytest.fixture
def exercise_entry_factory(session) -> ExerciseEntryFactory:
    return ExerciseEntryFactory(session)


@pytest.fixture
def unscramble_word_exercise_factory(
    session, exercise_factory, exercise_entry_factory
) -> UnscrambleWordExerciseFactory:
    return UnscrambleWordExerciseFactory(session, exercise_factory, exercise_entry_factory)
