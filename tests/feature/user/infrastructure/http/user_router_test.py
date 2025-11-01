from unittest.mock import AsyncMock
from fastapi import HTTPException
import pytest
from httpx import AsyncClient
from src.shared.enum import UserProvider
from src.user.infrastructure.oauth.login_strategy import GoogleLoginStrategy
from src.user.infrastructure.oauth.models import OAuthUser
from tests.factory import UserFactory


@pytest.mark.asyncio
async def test_login_success(user_factory: UserFactory, client: AsyncClient):
    await user_factory.create(email="test@example.com", password="secret1234")

    response = await client.post(
        "/api/user/login", json={"username": "test@example.com", "password": "secret1234"}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
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


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, user_factory: UserFactory):
    await user_factory.create(email="test@example.com", password="secret")

    response = await client.post(
        "/api/user/login", json={"username": "test5@example.com", "password": "wrong"}
    )

    assert response.status_code == 422
