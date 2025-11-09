from contextlib import asynccontextmanager
from core.db import init_db, close_db
from fastapi import FastAPI, Response
from core.db_session import db_session
from core.logging import exception_handler, log_response_time
from src.user.infrastructure.http.router import router as user_router
from src.flashcard.infrastructure.http.router import router as flashcard_router
from src.study.infrastructure.http.router import router as study_router
import uvicorn
from starlette.requests import Request
from core.open_api import custom_openapi
from core.logging import queue_listener


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
    queue_listener.stop()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next) -> Response:
    return await db_session(request, call_next)


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
