from punq import Container
import pytest
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.infrastructure.repository.flashcard_deck_read_repository import (
    FlashcardDeckReadRepository,
)
from src.shared.enum import Language
from src.shared.value_objects.user_id import UserId
from tests.factory import (
    FlashcardFactory,
    FlashcardDeckFactory,
    OwnerFactory,
)


@pytest.fixture
def repository(container: Container) -> FlashcardDeckReadRepository:
    return container.resolve(FlashcardDeckReadRepository)


@pytest.mark.asyncio
async def test_find_should_find_deck(
    repository: FlashcardDeckReadRepository,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
):
    user = await owner_factory.create_user_owner()
    deck = await deck_factory.create(user)
    flashcard = await flashcard_factory.create(deck, user)

    result = await repository.find_details(
        UserId(value=user.id.value), FlashcardDeckId(value=deck.id), None, 1, 15
    )

    assert result.count == 1
    assert result.language_level.value == deck.default_language_level
    assert result.flashcards[0].front_word == flashcard.front_word


@pytest.mark.asyncio
async def test_get_by_user(
    repository: FlashcardDeckReadRepository,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
):
    user = await owner_factory.create_user_owner()
    decks = [
        await deck_factory.create(user),
        await deck_factory.create(user),
    ]

    results = await repository.get_by_user(
        UserId(value=user.id.value), Language.PL, Language.EN, None, 1, 15
    )

    assert len(results) == 2
    assert set([result.id.get_value() for result in results]) == set([deck.id for deck in decks])


@pytest.mark.asyncio
async def test_get_by_admin(
    repository: FlashcardDeckReadRepository,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
):
    user = await owner_factory.create_user_owner()
    admin = await owner_factory.create_admin_owner()
    decks = [
        await deck_factory.create(user),
        await deck_factory.create(admin),
    ]

    results = await repository.get_admin_decks(
        UserId(value=user.id.value), Language.PL, Language.EN, None, None, 1, 15
    )

    assert len(results) == 1
    assert results[0].id.get_value() == decks[1].id
