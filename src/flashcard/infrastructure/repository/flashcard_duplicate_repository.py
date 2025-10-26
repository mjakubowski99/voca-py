from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.flashcard.domain.value_objects import FlashcardDeckId
from core.models import Flashcards
from core.db import get_session
from src.flashcard.application.repository.contracts import IFlashcardDuplicateRepository


class FlashcardDuplicateRepository(IFlashcardDuplicateRepository):
    async def get_already_saved_front_words(
        self, deck_id: FlashcardDeckId, front_words: list[str]
    ) -> list[str]:
        """
        Returns all front words already saved in the deck (case-insensitive).
        """
        # normalize to lowercase
        normalized_words = [word.lower() for word in front_words]

        session: AsyncSession = get_session()
        query = (
            select(Flashcards.front_word)
            .where(Flashcards.flashcard_deck_id == deck_id.value)
            .where(func.lower(Flashcards.front_word).in_(normalized_words))
        )
        result = await session.execute(query)
        # extract values from result
        return [row[0] for row in result.all()]

    async def get_random_front_word_initial_letters(
        self, deck_id: FlashcardDeckId, limit: int
    ) -> list[str]:
        """
        Returns unique first letters of random front words from the deck.
        """
        session: AsyncSession = get_session()
        query = (
            select(Flashcards.front_word)
            .where(Flashcards.flashcard_deck_id == deck_id.value)
            .order_by(func.random())
            .limit(limit)
        )
        result = await session.execute(query)
        front_words = [row[0] for row in result.all()]
        # get first letters, remove duplicates
        letters = list({word[0] for word in front_words if word})
        return letters
