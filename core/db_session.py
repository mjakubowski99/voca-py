from core.db import set_db_session_context
from fastapi import Response
from starlette.requests import Request
from core.db import get_session
import asyncio
from sqlalchemy.exc import OperationalError

from core.logging import logger


async def _commit_with_retry(session, retries=3, delay=0.1):
    for attempt in range(retries):
        try:
            await session.commit()
            return
        except OperationalError as e:
            if "deadlock" in str(e).lower() and attempt < retries - 1:
                await asyncio.sleep(delay)
                continue
            raise


async def db_session(request: Request, call_next):
    response = Response("Internal server error", status_code=500)

    try:
        set_db_session_context(session_id=hash(request))
        response = await call_next(request)
        await _commit_with_retry(get_session())

    except Exception:
        await get_session().rollback()
        raise
    finally:
        await get_session().close()
        set_db_session_context(session_id=None)
    return response
