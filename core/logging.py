from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.requests import Request
import time
import queue
import logging
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
import traceback
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

log_queue = queue.Queue()
# Non-blocking handler.
queue_handler = QueueHandler(log_queue)

queue_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Attached to the root logger.
logger.addHandler(queue_handler)

# The blocking handler.
rot_handler = RotatingFileHandler("logs/api.log")

# Sitting comfortably in its own thread, isolated from async code.
queue_listener = QueueListener(log_queue, rot_handler)

# Start listening.
queue_listener.start()


def log_to_span(message: str, level: int = logging.INFO):
    span = trace.get_current_span()
    if span and span.is_recording():
        span.add_event(message, {"log.level": logging.getLevelName(level)})


async def log_response_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    logger.info(
        f"{request.method} {request.url.path} | "
        f"{process_time:.4f}s | "
        f"Status: {response.status_code}"
    )

    return response


async def exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (RequestValidationError, ValidationError)):
        detail = exc.errors()
    else:
        detail = str(exc)

    tb_str = traceback.format_exc()
    log_msg = (
        f"ERROR {request.method} {request.url.path}\n"
        f"Exception type: {exc.__class__.__name__}\n"
        f"Detail: {detail}\n"
        f"Traceback:\n{tb_str}"
    )

    logger.error(log_msg)
    log_to_span(log_msg, logging.ERROR)

    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"},
    )
