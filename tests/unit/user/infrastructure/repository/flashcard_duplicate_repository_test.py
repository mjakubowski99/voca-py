import pytest

from core.models import FlashcardDecks
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.infrastructure.repository.flashcard_duplicate_repository import (
    FlashcardDuplicateRepository,
)
from tests.factory import (
    create_flashcard_deck,
    create_user_owner,
    create_flashcard,
)
from core.container import container


def get_duplicate_repo() -> FlashcardDuplicateRepository:
    return container.resolve(FlashcardDuplicateRepository)


@pytest.mark.asyncio
async def test_get_already_saved_front_words(session):
    owner: Owner = await create_user_owner(session)
    deck: FlashcardDecks = await create_flashcard_deck(session, owner=owner)

    # Add flashcards
    words = ["Apple", "Banana", "Cherry"]
    for word in words:
        await create_flashcard(deck=deck, owner=owner, front_word=word, session=session)

    # Test duplicate repository
    duplicates = await get_duplicate_repo().get_already_saved_front_words(
        FlashcardDeckId(value=deck.id), ["banana", "Durian", "APPLE"]
    )

    # Should return only existing front words (case-insensitive)
    assert set(duplicates) == {"Apple", "Banana"}


@pytest.mark.asyncio
async def test_get_random_front_word_initial_letters(session):
    # Create deck
    owner: Owner = await create_user_owner(session)
    deck: FlashcardDecks = await create_flashcard_deck(session, owner=owner)

    # Add flashcards
    words = ["Apple", "Banana", "Avocado", "Cherry"]
    for word in words:
        await create_flashcard(deck=deck, owner=owner, front_word=word, session=session)

    # Test random initial letters
    letters = await get_duplicate_repo().get_random_front_word_initial_letters(
        FlashcardDeckId(value=deck.id), limit=3
    )

    # Letters should be subset of first letters of all words
    expected_letters = {word[0] for word in words}
    assert set(letters).issubset(expected_letters)
