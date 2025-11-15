from unittest.mock import AsyncMock
from fastapi import HTTPException
import pytest
from httpx import AsyncClient
from core.models import (
    FlashcardDecks,
    FlashcardPollItems,
    Flashcards,
    LearningSessionFlashcards,
    LearningSessions,
    Users,
)
from src.flashcard.domain.models.owner import Owner
from src.shared.enum import UserProvider
from src.shared.value_objects.user_id import UserId
from src.user.infrastructure.oauth.login_strategy import GoogleLoginStrategy
from src.user.infrastructure.oauth.models import OAuthUser
from tests.factory import (
    FlashcardDeckFactory,
    FlashcardFactory,
    FlashcardPollItemFactory,
    LearningSessionFactory,
    LearningSessionFlashcardFactory,
    UserFactory,
)


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


@pytest.mark.asyncio
async def test_delete_user_success(
    client: AsyncClient,
    user_factory: UserFactory,
    flashcard_factory: FlashcardFactory,
    deck_factory: FlashcardDeckFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    assert_db_missing,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner.from_user(UserId(value=user.id))
    deck = await deck_factory.create(owner)
    flashcard = await flashcard_factory.create(deck, owner)
    session = await learning_session_factory.create(user.id)
    learning_session_flashcard = await learning_session_flashcard_factory.create(session, flashcard)

    client.login(user)
    response = await client.client.request(
        "DELETE", "/api/v2/user/me", json={"email": "test@example.com"}
    )

    assert response.status_code == 200
    await assert_db_missing(Users, {"id": user.id})
    await assert_db_missing(Flashcards, {"id": flashcard.id})
    await assert_db_missing(FlashcardDecks, {"id": deck.id})
    await assert_db_missing(LearningSessions, {"id": session.id})
    await assert_db_missing(LearningSessionFlashcards, {"id": learning_session_flashcard.id})


@pytest.mark.asyncio
async def test_update_language_success(
    client: AsyncClient,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    flashcard_poll_factory: FlashcardPollItemFactory,
    assert_db_has,
    assert_db_missing,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner.from_user(UserId(value=user.id))
    deck = await deck_factory.create(owner)
    flashcard = await flashcard_factory.create(deck, owner)
    flashcard_poll_item = await flashcard_poll_factory.create(user.id, flashcard.id)

    client.login(user)
    response = await client.client.request(
        "PUT", "/api/v2/user/me/language", json={"user_language": "en", "learning_language": "pl"}
    )

    assert response.status_code == 200
    await assert_db_has(Users, {"id": user.id, "user_language": "en", "learning_language": "pl"})
    await assert_db_missing(FlashcardPollItems, {"id": flashcard_poll_item.id})
