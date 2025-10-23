from fastapi import Depends, FastAPI, HTTPException
from fastapi import Body, FastAPI
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from config import settings
from src.entry.container import container
from src.shared.user.iuser import IUser

from src.user.infrastructure.http.router import router as user_router
from fastapi.openapi.utils import get_openapi
import uvicorn

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

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
        "src.main:app",           # <— use import string, not the variable directly
        host="0.0.0.0",
        port=8000,
        reload=True,              # enables live reload when files change
        log_level="info"
    )