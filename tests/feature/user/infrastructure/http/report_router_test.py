import pytest
from tests.conftest import HttpClient
from tests.factory import UserFactory


@pytest.mark.asyncio
async def test_create_report_success(client: HttpClient, user_factory: UserFactory):
    user = await user_factory.create()
    client.login(user)
    response = await client.post(
        "/api/v2/reports",
        json={
            "email": "test@example.com",
            "type": "inappropriate_content",
            "description": "This flashcard has inappropriate content",
        },
    )
    assert response.status_code == 200
    assert response.json()["id"] is not None
