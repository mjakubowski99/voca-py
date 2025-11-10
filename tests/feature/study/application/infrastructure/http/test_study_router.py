import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import LearningSessionFlashcards, SmTwoFlashcards
from src.study.domain.enum import Rating, SessionType
from tests.client import HttpClient
from tests.factory import LearningSessionFactory, LearningSessionFlashcardFactory, UserFactory
from tests.factory import FlashcardDeckFactory, FlashcardFactory
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import OwnerId
from src.flashcard.domain.enum import FlashcardOwnerType


@pytest.mark.asyncio
async def test_create_session_success(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    dump,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    await flashcard_factory.create(deck=deck, owner=owner)
    await flashcard_factory.create(deck=deck, owner=owner)

    client.login(user)
    response = await client.post(
        "/api/v2/flashcards/session",
        json={
            "session_type": "flashcard",
            "flashcard_deck_id": deck.id,
            "cards_per_session": 10,
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_session_when_unscramble_success(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    dump,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    await flashcard_factory.create(deck=deck, owner=owner)
    await flashcard_factory.create(deck=deck, owner=owner)

    client.login(user)
    response = await client.post(
        "/api/v2/flashcards/session",
        json={
            "session_type": SessionType.UNSCRAMBLE_WORDS,
            "flashcard_deck_id": deck.id,
            "cards_per_session": 10,
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_flashcard_success(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    assert_db_has,
    dump_db,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)
    learning_session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=learning_session, flashcard=flashcard
    )
    client.login(user)
    response = await client.put(
        f"/api/v2/flashcards/session/{learning_session.id}/rate-flashcard",
        json={"ratings": [{"id": session_step.id, "rating": Rating.VERY_GOOD.value}]},
    )

    assert response.status_code == 200
    await assert_db_has(
        LearningSessionFlashcards, {"id": session_step.id, "rating": Rating.VERY_GOOD.value}
    )
    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "last_rating": Rating.VERY_GOOD.value,
            "repetition_interval": 6.0,
        },
    )
