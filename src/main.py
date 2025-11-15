from contextlib import asynccontextmanager

from core.database import Database
from fastapi import FastAPI, Response
from core.logging import exception_handler, log_response_time
from core.opentelemetry import handle_tracing
from src.user.infrastructure.http.router import router as user_router
from src.user.infrastructure.http.report_router import router as report_router
from src.flashcard.infrastructure.http.router import router as flashcard_router
from src.study.infrastructure.http.router import router as study_router
import uvicorn
from starlette.requests import Request
from core.open_api import custom_openapi
from core.logging import queue_listener
from config import settings
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
import core.database as database
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "*",
]

_already_instrumented = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _already_instrumented

    database.db = Database(settings.database_url)

    if not _already_instrumented:
        FastAPIInstrumentor.instrument_app(app, server_request_hook=server_request_naming_hook)
        SQLAlchemyInstrumentor().instrument(engine=database.db.engine.sync_engine)
        _already_instrumented = True

    yield

    if database.db:
        await database.db.close()

    queue_listener.stop()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def tracing_middleware(request: Request, call_next):
    return await handle_tracing(request, call_next)


def server_request_naming_hook(span, scope):
    """Rename spans automatically to reflect route names like GET /users/{id}"""
    if span and scope:
        method = scope.get("method", "GET")
        route = scope.get("path", "<unknown>")
        span.update_name(f"{method} {route}")
        span.set_attribute("http.route", route)
        span.set_attribute("http.method", method)


@app.middleware("http")
async def logging(request: Request, call_next) -> Response:
    return await log_response_time(request, call_next)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await exception_handler(request, exc)


app.openapi = lambda: custom_openapi(app)
app.include_router(user_router)
app.include_router(report_router)
app.include_router(flashcard_router)
app.include_router(study_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=60,
    )
