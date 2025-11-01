from config import settings
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_scoped_session,
    async_sessionmaker,
    AsyncSession,
)
from contextvars import ContextVar

db_session_context: ContextVar[int | None] = ContextVar("db_session_context", default=None)

engine = None
AsyncLocalSession = None


def set_db_session_context(session_id: int | None) -> None:
    db_session_context.set(session_id)


def get_db_session_context() -> int:
    session_id = db_session_context.get()
    if session_id is None:
        raise ValueError("No session available")
    return session_id


def get_session() -> AsyncSession:
    if AsyncLocalSession is None:
        raise RuntimeError("Database session not initialized")
    return AsyncLocalSession()


async def init_db():
    global engine, AsyncLocalSession
    engine = create_async_engine(settings.database_url, echo=True)
    AsyncLocalSession = async_scoped_session(
        session_factory=async_sessionmaker(bind=engine, autoflush=False, autocommit=False),
        scopefunc=get_db_session_context,
    )


async def close_db():
    global engine
    if engine:
        await engine.dispose()
