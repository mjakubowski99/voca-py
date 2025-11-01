from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from core.models import Flashcards, Stories, StoryFlashcards
from src.flashcard.domain.models.owner import Owner
from src.shared.value_objects.user_id import UserId
from tests.client import HttpClient
from tests.fixtures.api_response import *
from unittest.mock import AsyncMock, MagicMock, patch
from tests.factory import (
    FlashcardDeckFactory,
    OwnerFactory,
    UserFactory,
)
import pytest


@pytest.mark.asyncio
async def test_generate_should_generate_new_flashcards(
    session: AsyncSession,
    gemini_flashcards_generate_response: str,
    client: HttpClient,
    user_factory: UserFactory,
    assert_db_count,
):
    fake_response = MagicMock()
    fake_response.text = gemini_flashcards_generate_response
    fake_client = MagicMock()
    fake_client.models.generate_content = AsyncMock(return_value=fake_response)

    user = await user_factory.create()

    class FakeAioContext:
        async def __aenter__(self):
            return fake_client

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

    fake_client.aio = FakeAioContext()

    with patch(
        "src.flashcard.application.services.gemini_generator.Client",
        return_value=fake_client,
    ):
        client.login(user)
        response = await client.post(
            "/api/v2/flashcards/decks/generate-flashcards",
            json={"category_name": "New flashcards", "language_level": "A1"},
            headers={"Authorization": "Bearer token"},
        )

    await assert_db_count(Flashcards, 10, {"flashcard_deck_id": response.json()["data"][0]["id"]})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_generate_should_generate_new_flashcards_belonging_to_stories(
    session: AsyncSession,
    gemini_flashcards_with_stories_generate_response,
    client: HttpClient,
    user_factory: UserFactory,
    assert_db_count,
):
    fake_response = MagicMock()
    fake_response.text = gemini_flashcards_with_stories_generate_response
    fake_client = MagicMock()
    fake_client.models.generate_content = AsyncMock(return_value=fake_response)

    user = await user_factory.create()

    class FakeAioContext:
        async def __aenter__(self):
            return fake_client

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

    fake_client.aio = FakeAioContext()

    with patch(
        "src.flashcard.application.services.gemini_generator.Client",
        return_value=fake_client,
    ):
        client.login(user)
        response = await client.post(
            "/api/v2/flashcards/decks/generate-flashcards",
            json={"category_name": "New flashcards", "language_level": "A1"},
            headers={"Authorization": "Bearer token"},
        )

    assert response.status_code == 200

    stmt = (
        select(StoryFlashcards, Flashcards.back_word)
        .join(Flashcards, Flashcards.id == StoryFlashcards.flashcard_id)
        .where(Flashcards.flashcard_deck_id == response.json()["data"][0]["id"])
    )

    result = await session.execute(stmt)
    flashcards = result.all()

    expected_stories = {
        1: ["pet food", "litter", "collar"],
        2: ["leash", "harness"],
        3: ["toy", "aquarium"],
        4: ["cage", "brush", "carrier"],
    }

    # Zbuduj mapę story_id -> lista słów z bazy
    story_words_map = {}
    for f in flashcards:
        story_words_map.setdefault(f[0].story_id, []).append(f[1])

    # Utwórz listę zbiorów słów (ignorujemy konkretne ID)
    actual_story_sets = [set(words) for words in story_words_map.values()]
    expected_story_sets = [set(words) for words in expected_stories.values()]

    # ✅ Sprawdź, że każde oczekiwane story ma dokładnie taki zestaw słów jak któreś ze story w bazie
    for expected_set in expected_story_sets:
        assert expected_set in actual_story_sets, (
            f"Nie znaleziono story z flashcards: {expected_set}"
        )
    await assert_db_count(Stories, 4, {})
    await assert_db_count(StoryFlashcards, 10, {})


@pytest.mark.asyncio
async def test_get_user_decks_return_user_decks(
    client: HttpClient, user_factory: UserFactory, deck_factory: FlashcardDeckFactory
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))

    await deck_factory.create(owner)
    await deck_factory.create(owner)

    client.login(user)
    response = await client.get(
        "/api/v2/flashcards/decks/by-user",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_admin_decks_return_admin_decks_for_user(
    client: HttpClient,
    user_factory: UserFactory,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
):
    admin = await owner_factory.create_admin_owner()
    user = await user_factory.create()

    await deck_factory.create(admin)
    await deck_factory.create(admin)

    client.login(user)

    response = await client.get(
        "/api/v2/flashcards/decks/by-admin",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
