import pytest
from punq import Container
from core.models import FlashcardDecks
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.infrastructure.repository.flashcard_duplicate_repository import (
    FlashcardDuplicateRepository,
)
from tests.factory import FlashcardDeckFactory, FlashcardFactory, OwnerFactory


@pytest.fixture
def repository(container: Container) -> FlashcardDuplicateRepository:
    return container.resolve(FlashcardDuplicateRepository)


@pytest.mark.asyncio
async def test_get_already_saved_front_words(
    repository: FlashcardDuplicateRepository,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
):
    owner: Owner = await owner_factory.create_user_owner()
    deck: FlashcardDecks = await deck_factory.create(owner=owner)

    # Add flashcards
    words = ["Apple", "Banana", "Cherry"]
    for word in words:
        await flashcard_factory.create(deck=deck, owner=owner, front_word=word)

    # Test duplicate repository
    duplicates = await repository.get_already_saved_front_words(
        FlashcardDeckId(value=deck.id), ["banana", "Durian", "APPLE"]
    )

    # Should return only existing front words (case-insensitive)
    assert set(duplicates) == {"Apple", "Banana"}


@pytest.mark.asyncio
async def test_get_random_front_word_initial_letters(
    repository: FlashcardDuplicateRepository,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
):
    # Create deck
    owner: Owner = await owner_factory.create_user_owner()
    deck: FlashcardDecks = await deck_factory.create(owner=owner)

    # Add flashcards
    words = ["Apple", "Banana", "Avocado", "Cherry"]
    for word in words:
        await flashcard_factory.create(deck=deck, owner=owner, front_word=word)

    # Test random initial letters
    letters = await repository.get_random_front_word_initial_letters(
        FlashcardDeckId(value=deck.id), limit=3
    )

    # Letters should be subset of first letters of all words
    expected_letters = {word[0] for word in words}
    assert set(letters).issubset(expected_letters)
