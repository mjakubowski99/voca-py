import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.infrastructure.repository.flashcard_deck_read_repository import (
    FlashcardDeckReadRepository,
)
from core.container import container
from src.shared.value_objects.user_id import UserId
from tests.factory import create_flashcard, create_flashcard_deck, create_user_owner


def get_repo() -> FlashcardDeckReadRepository:
    return container.resolve(FlashcardDeckReadRepository)


@pytest.mark.asyncio
async def test_find_should_find_eck(session: AsyncSession):
    user = await create_user_owner(session)

    deck = await create_flashcard_deck(session, user)
    flashcard = await create_flashcard(session, deck, user)

    result = await get_repo().find_details(
        UserId(value=user.id.value), FlashcardDeckId(value=deck.id), None, 1, 15
    )

    assert result.count == 1
    assert result.language_level.value == deck.default_language_level
    assert result.flashcards[0].front_word == flashcard.front_word
