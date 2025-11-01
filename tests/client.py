from typing import Optional
from httpx import AsyncClient
from unittest.mock import Mock
from core.models import Users
from src.shared.user.iuser import IUser
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId
from core.auth import get_current_user
from src.main import app


class HttpClient:
    """Wrapper around AsyncClient with authentication support."""

    def __init__(self, client: AsyncClient, monkeypatch):
        self.client = client
        self.monkeypatch = monkeypatch
        self._current_user: Optional[Users] = None

    def login(self, user: Users):
        """Login as specific user."""
        user_mock = Mock(spec=IUser)
        user_mock.get_id.return_value = UserId(value=user.id)
        user_mock.get_email.return_value = user.email
        user_mock.get_name.return_value = user.name
        user_mock.get_learning_language.return_value = Language(value=user.learning_language)
        user_mock.get_user_language.return_value = Language(value=user.user_language)

        async def _current_user():
            return user_mock

        app.dependency_overrides[get_current_user] = _current_user
        self._current_user = user
        return self

    def logout(self):
        """Clear authentication."""
        app.dependency_overrides.pop(get_current_user, None)
        self._current_user = None
        return self

    # Proxy all AsyncClient methods
    async def get(self, *args, **kwargs):
        return await self.client.get(*args, **kwargs)

    async def post(self, *args, **kwargs):
        return await self.client.post(*args, **kwargs)

    async def put(self, *args, **kwargs):
        return await self.client.put(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        return await self.client.delete(*args, **kwargs)

    async def patch(self, *args, **kwargs):
        return await self.client.patch(*args, **kwargs)
