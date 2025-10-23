import pytest
from httpx import AsyncClient
from tests.factory import create_user
from tests.conftest import client

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session):
    user = await create_user(db_session, email="test@example.com", password="secret1234")

    response = await client.post(
        "/api/user/login",
        json={"username": "test@example.com", "password": "secret1234"}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, db_session):
    user = await create_user(db_session, email="test@example.com", password="secret")

    response = await client.post(
        "/api/user/login",
        json={"username": "test@example.com", "password": "wrong"}
    )

    assert response.status_code == 422
