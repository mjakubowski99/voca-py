from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from core.models import FlashcardDecks, Flashcards, Stories, StoryFlashcards
from src.flashcard.domain.models.owner import Owner
from src.shared.value_objects.user_id import UserId
from src.study.domain.enum import Rating
from tests.client import HttpClient
from unittest.mock import AsyncMock, MagicMock, patch
from tests.factory import (
    FlashcardDeckFactory,
    FlashcardFactory,
    LearningSessionFactory,
    LearningSessionFlashcardFactory,
    OwnerFactory,
    UserFactory,
)
import pytest
from tests.fixtures.api_response import *


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

    await assert_db_count(Flashcards, 10, {"flashcard_deck_id": response.json()["data"]["id"]})
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
        .where(Flashcards.flashcard_deck_id == response.json()["data"]["id"])
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
        "/api/v2/flashcards/decks/by-admins",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_flashcard_should_create_flashcard(
    client: HttpClient,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    assert_db_has,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    deck = await deck_factory.create(owner)

    client.login(user)
    response = await client.post(
        "/api/v2/flashcards",
        json={
            "flashcard_deck_id": deck.id,
            "front_word": "cat",
            "back_word": "kot",
            "front_context": "The cat is sleeping",
            "back_context": "Kot leży na kanapie",
            "language_level": "A1",
            "emoji": "🐱",
        },
    )

    assert response.status_code == 200
    await assert_db_has(
        Flashcards,
        {
            "flashcard_deck_id": deck.id,
            "front_word": "cat",
            "back_word": "kot",
            "front_context": "The cat is sleeping",
            "back_context": "Kot leży na kanapie",
            "language_level": "A1",
            "emoji": "🐱",
            "user_id": user.id,
            "admin_id": None,
        },
    )


@pytest.mark.asyncio
async def test_update_flashcard_should_update_flashcard(
    client: HttpClient,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    assert_db_has,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    deck = await deck_factory.create(owner)
    flashcard = await flashcard_factory.create(deck, owner)

    client.login(user)
    response = await client.put(
        f"/api/v2/flashcards/{flashcard.id}",
        json={
            "flashcard_deck_id": deck.id,
            "front_word": "dog",
            "back_word": "pies",
            "front_context": "The dog is barking",
            "back_context": "Pies szczeka",
            "language_level": "A1",
            "emoji": "🐶",
        },
    )

    assert response.status_code == 200
    await assert_db_has(
        Flashcards,
        {
            "flashcard_deck_id": deck.id,
            "front_word": "dog",
            "back_word": "pies",
            "front_context": "The dog is barking",
            "back_context": "Pies szczeka",
            "language_level": "A1",
            "emoji": "🐶",
            "user_id": user.id,
            "admin_id": None,
        },
    )


@pytest.mark.asyncio
async def test_bulk_delete_flashcards_should_delete_flashcards(
    client: HttpClient,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    assert_db_missing,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    deck = await deck_factory.create(owner)
    flashcard = await flashcard_factory.create(deck, owner)

    client.login(user)
    response = await client.client.request(
        "DELETE",
        url="/api/v2/flashcards/bulk-delete",
        json={"flashcard_ids": [flashcard.id]},
    )

    assert response.status_code == 200
    await assert_db_missing(Flashcards, {"id": flashcard.id})


@pytest.mark.asyncio
async def test_merge_decks_should_merge_decks(
    client: HttpClient,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    assert_db_has,
    assert_db_missing,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    deck1 = await deck_factory.create(owner)
    deck2 = await deck_factory.create(owner)
    flashcard = await flashcard_factory.create(deck1, owner)

    client.login(user)
    response = await client.post(
        f"/api/v2/flashcards/decks/{deck1.id}/merge/{deck2.id}",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    await assert_db_missing(FlashcardDecks, {"id": deck1.id})
    await assert_db_has(FlashcardDecks, {"id": deck2.id})


@pytest.mark.asyncio
async def test_get_rating_stats_for_deck_should_return_rating_stats(
    client: HttpClient,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    dump,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    deck = await deck_factory.create(owner)
    flashcard = await flashcard_factory.create(deck, owner)
    session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=session, flashcard=flashcard, rating=Rating.VERY_GOOD
    )

    client.login(user)
    response = await client.get(
        f"/api/v2/flashcards/decks/{deck.id}/rating-stats",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_rating_stats_for_user_should_return_rating_stats(
    client: HttpClient,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    dump,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    deck = await deck_factory.create(owner)
    flashcard = await flashcard_factory.create(deck, owner)
    session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=session, flashcard=flashcard, rating=Rating.VERY_GOOD
    )

    client.login(user)
    response = await client.get(
        f"/api/v2/flashcards/by-user/rating-stats",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_rating_stats_for_admin_should_return_rating_stats(
    client: HttpClient,
    user_factory: UserFactory,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    dump,
):
    user = await user_factory.create()
    admin = await owner_factory.create_admin_owner()
    deck = await deck_factory.create(admin)
    flashcard = await flashcard_factory.create(deck, admin)
    session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=session, flashcard=flashcard, rating=Rating.VERY_GOOD
    )

    client.login(user)
    response = await client.get(
        f"/api/v2/flashcards/by-admin/rating-stats",
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
