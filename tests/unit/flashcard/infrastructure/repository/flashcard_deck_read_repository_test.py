import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.infrastructure.repository.flashcard_deck_read_repository import (
    FlashcardDeckReadRepository,
)
from core.container import container
from src.shared.enum import Language, LanguageLevel
from src.shared.value_objects.user_id import UserId
from tests.factory import (
    FlashcardFactory,
    FlashcardDeckFactory,
    OwnerFactory,
)


def get_repo() -> FlashcardDeckReadRepository:
    return container.resolve(FlashcardDeckReadRepository)


@pytest.mark.asyncio
async def test_find_should_find_deck(
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
):
    user = await owner_factory.create_user_owner()
    deck = await deck_factory.create(user)
    flashcard = await flashcard_factory.create(deck, user)

    result = await get_repo().find_details(
        UserId(value=user.id.value), FlashcardDeckId(value=deck.id), None, 1, 15
    )

    assert result.count == 1
    assert result.language_level.value == deck.default_language_level
    assert result.flashcards[0].front_word == flashcard.front_word


@pytest.mark.asyncio
async def test_get_by_user(
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
):
    user = await owner_factory.create_user_owner()
    decks = [
        await deck_factory.create(user),
        await deck_factory.create(user),
    ]

    results = await get_repo().get_by_user(
        UserId(value=user.id.value), Language.PL, Language.EN, None, 1, 15
    )

    assert len(results) == 2
    assert results[1].id.get_value() == decks[0].id
    assert results[0].id.get_value() == decks[1].id


@pytest.mark.asyncio
async def test_get_by_admin(
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
):
    user = await owner_factory.create_user_owner()
    admin = await owner_factory.create_admin_owner()
    decks = [
        await deck_factory.create(user),
        await deck_factory.create(admin),
    ]

    results = await get_repo().get_admin_decks(
        UserId(value=user.id.value), Language.PL, Language.EN, None, None, 1, 15
    )

    assert len(results) == 1
    assert results[0].id.get_value() == decks[1].id
