import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.flashcard.domain.models.deck import Deck
from tests.factory import OwnerFactory, FlashcardDeckFactory
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.infrastructure.repository.flashcard_deck_repository import (
    FlashcardDeckRepository,
)
from src.shared.enum import LanguageLevel
from core.container import container


def get_repo() -> FlashcardDeckRepository:
    return container.resolve(FlashcardDeckRepository)


@pytest.mark.asyncio
async def test_create_should_create_new_deck(owner_factory: OwnerFactory):
    deck = Deck(
        owner=await owner_factory.create_user_owner(),
        name="Example deck",
        tag="Example deck",
        default_language_level=LanguageLevel.B2,
    )

    result = await get_repo().create(deck)

    assert isinstance(result, FlashcardDeckId)


@pytest.mark.asyncio
async def test_find_by_id_should_return_deck(
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
):
    repo: FlashcardDeckRepository = get_repo()

    # Use the factory to create a deck
    owner = await owner_factory.create_user_owner()
    deck = await deck_factory.create(owner=owner)

    # Fetch the deck by ID
    fetched_deck = await repo.find_by_id(FlashcardDeckId(value=deck.id))

    # Assertions
    assert fetched_deck.name == deck.name
    assert fetched_deck.tag == deck.tag
    assert fetched_deck.default_language_level == deck.default_language_level


@pytest.mark.asyncio
async def test_find_by_id_should_raise_if_not_found():
    repo: FlashcardDeckRepository = get_repo()

    invalid_id = FlashcardDeckId(value=100000000)

    with pytest.raises(ValueError, match="Deck not found"):
        await repo.find_by_id(invalid_id)
