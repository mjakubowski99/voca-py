from asyncio.log import logger
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi import Body, FastAPI
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config import settings
from src.entry.container import container
from src.shared.user.iuser import IUser
from src.user.infrastructure.http.router import router as user_router
from fastapi.openapi.utils import get_openapi
import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.entry.db import AsyncLocalSession, set_db_session_context, get_session
import asyncio
from sqlalchemy.exc import OperationalError
from src.entry.db import init_db, close_db

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on application startup"""
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool on application shutdown"""
    await close_db()

@app.middleware("http")
async def db_session_middleware_function(
    request: Request, call_next
):
    await init_db()
    response = Response(
        "Internal server error", status_code=500
    )
    try:
        set_db_session_context(session_id=hash(request))
        response = await call_next(request)
        await _commit_with_retry(get_session())
    finally:
        set_db_session_context(session_id=None)
    return response

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI application",
        version="1.0.0",
        description="JWT Authentication and Authorization",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )