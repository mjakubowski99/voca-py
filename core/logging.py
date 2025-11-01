from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.requests import Request
import time
import queue
import logging
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
import traceback

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

    # Log structured error message with traceback
    logger.error(
        f"ERROR {request.method} {request.url.path}\n"
        f"Exception type: {exc.__class__.__name__}\n"
        f"Detail: {detail}\n"
        f"Traceback:\n{traceback.format_exc()}",
        exc_info=False,  # no need for double traceback
    )

    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"},
    )
