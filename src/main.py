from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import Database
from fastapi import Depends, FastAPI, Response
from core.container import create_container
from core.logging import exception_handler, log_response_time
from src.user.infrastructure.http.router import router as user_router
from src.flashcard.infrastructure.http.router import router as flashcard_router
from src.study.infrastructure.http.router import router as study_router
import uvicorn
from starlette.requests import Request
from core.open_api import custom_openapi
from core.logging import queue_listener
from config import settings
from punq import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db

    db = Database(settings.database_url)

    yield

    if db:
        await db.close()

    queue_listener.stop()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def logging(request: Request, call_next) -> Response:
    return await log_response_time(request, call_next)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await exception_handler(request, exc)


app.openapi = lambda: custom_openapi(app)
app.include_router(user_router)
app.include_router(flashcard_router)
app.include_router(study_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
