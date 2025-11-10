from punq import Container
import pytest
from rich.console import Console
from rich.table import Table
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import AsyncClient, ASGITransport
from sqlalchemy import event
from core.models import Base
from src.main import app
from core.database import get_session
from core.container import create_container
from config import settings
from tests.client import HttpClient
from tests.factory import (
    UserFactory,
    AdminFactory,
    OwnerFactory,
    FlashcardDeckFactory,
    FlashcardFactory,
    SmTwoFlashcardsFactory,
    FlashcardPollItemFactory,
    ExerciseFactory,
    ExerciseEntryFactory,
    UnscrambleWordExerciseFactory,
    WordMatchExerciseFactory,
    LearningSessionFactory,
    LearningSessionFlashcardFactory,
)
from src.shared.util.hash import IHash
from tests.asserts import *

console = Console(force_terminal=True)
TEST_DB_URL = settings.database_url


# ---------------------------
# Backend for anyio / asyncio
# ---------------------------
@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


# ---------------------------
# Console dumping helper
# ---------------------------
@pytest.fixture(autouse=True)
def dump(capsys):
    def _dump(value):
        with capsys.disabled():
            console.print()
            console.print(value, style="bold green")

    return _dump


@pytest.fixture
def dump_db(dump, session):
    async def _dump_db(model: type, limit: int = 20):
        result = await session.execute(model.select().limit(limit))
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


# ---------------------------
# Engine / Session fixtures
# ---------------------------
@pytest.fixture(scope="session")
def test_engine():
    return create_async_engine(TEST_DB_URL, echo=False)


@pytest.fixture(scope="session")
def async_session_maker(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database(test_engine):
    """
    Create tables if they don't exist and truncate all tables
    once before the test session starts.
    """
    async with test_engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

        # Truncate all tables
        table_names = ", ".join(
            [
                f'"{t.schema}"."{t.name}"' if t.schema else f'"{t.name}"'
                for t in Base.metadata.sorted_tables
            ]
        )
        if table_names:
            await conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE;"))

    yield  # Database prepared for tests


@pytest.fixture
async def session():
    # Create engine per test loop
    engine = create_async_engine(TEST_DB_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Open a connection and a transaction
    async with engine.connect() as conn:
        trans = await conn.begin()  # Outer transaction
        try:
            # Start a nested transaction (SAVEPOINT)
            async with async_session(bind=conn) as session:
                nested = await session.begin_nested()

                # Listen for session commits to restart SAVEPOINT
                @event.listens_for(session.sync_session, "after_transaction_end")
                def restart_savepoint(sess, trans_):
                    if trans_.nested and not trans_.is_active:
                        # restart nested transaction after commit
                        sess.begin_nested()

                yield session

                # Nested rollback happens automatically
        finally:
            await trans.rollback()
            await conn.close()

    await engine.dispose()


@pytest.fixture
def container(session: AsyncSession) -> Container:
    return create_container(session)


# ---------------------------
# Application / feature test client
# ---------------------------
@pytest.fixture
async def test_app(session: AsyncSession):
    """Override FastAPI get_session dependency to use test session."""

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def client(test_app, monkeypatch):
    """HTTP client using the app with overridden session."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://localhost",
    ) as async_client:
        yield HttpClient(client=async_client, monkeypatch=monkeypatch)


# ---------------------------
# Hasher and factories
# ---------------------------
@pytest.fixture
def hasher(container: Container) -> IHash:
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


@pytest.fixture
def word_match_exercise_factory(
    session, exercise_factory, exercise_entry_factory
) -> WordMatchExerciseFactory:
    return WordMatchExerciseFactory(session, exercise_factory, exercise_entry_factory)


@pytest.fixture
def learning_session_factory(
    session, owner_factory: OwnerFactory, deck_factory: FlashcardDeckFactory
) -> LearningSessionFactory:
    return LearningSessionFactory(session, owner_factory=owner_factory, deck_factory=deck_factory)


@pytest.fixture
def learning_session_flashcard_factory(session) -> LearningSessionFlashcardFactory:
    return LearningSessionFlashcardFactory(session)
