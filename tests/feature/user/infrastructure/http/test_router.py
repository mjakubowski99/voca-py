from unittest.mock import AsyncMock
from fastapi import HTTPException
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.enum import UserProvider
from src.user.infrastructure.oauth.login_strategy import GoogleLoginStrategy
from src.user.infrastructure.oauth.models import OAuthUser
from tests.factory import create_user

pytestmark = pytest.mark.anyio


async def test_login_success(session: AsyncSession, client):
    await create_user(session, email="test@example.com", password="secret1234")

    response = await client.post(
        "/api/user/login", json={"username": "test@example.com", "password": "secret1234"}
    )

    assert response.status_code == 200


async def test_google_login_success(monkeypatch, client: AsyncClient):
    # Fake OAuthUser
    fake_user = OAuthUser(
        id="123",
        user_provider=UserProvider.GOOGLE,
        name="Test User",
        email="test2@example.com",
        nickname="test@example.com",
        avatar="http://avatar.url",
    )

    # Async mock the user_from_token method
    async_mock = AsyncMock(return_value=fake_user)
    monkeypatch.setattr(GoogleLoginStrategy, "user_from_token", async_mock)

    response = await client.post(
        "/api/user/oauth/login",
        json={"access_token": "fake-token", "user_provider": "google", "platform": "web"},
    )

    assert response.status_code == 200


async def test_google_login_invalid_token(monkeypatch, client: AsyncClient):
    async def raise_exception(self, token: str):
        raise HTTPException(status_code=401, detail="Invalid token")

    monkeypatch.setattr(GoogleLoginStrategy, "user_from_token", raise_exception)

    response = await client.post(
        "/api/user/oauth/login",
        json={"access_token": "fake-token", "user_provider": "google", "platform": "web"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


async def test_login_invalid_password(session: AsyncSession, client):
    await create_user(session, email="test@example.com", password="secret")

    response = await client.post(
        "/api/user/login", json={"username": "test5@example.com", "password": "wrong"}
    )

    assert response.status_code == 422
