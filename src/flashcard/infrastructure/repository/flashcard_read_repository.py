from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from src.flashcard.application.dto.flashcard_read import FlashcardRead
from src.flashcard.application.dto.general_rating import GeneralRating
from src.flashcard.domain.enum import FlashcardOwnerType, GeneralRatingType
from src.flashcard.domain.models.emoji import Emoji
from src.flashcard.domain.value_objects import FlashcardDeckId, FlashcardId
from core.db import get_session

from core.models import Flashcards as FlashcardDB

# Placeholders for ORM models
from src.flashcard.domain.models.flashcard import Flashcard
from src.shared.value_objects.language import Language


class FlashcardReadRepository:
    async def find_by_deck(
        self, deck_id: FlashcardDeckId, search: Optional[str], page: int, per_page: int
    ) -> List[Flashcard]:
        flashcards = await self._fetch_flashcards(deck_id, search, page, per_page)
        result = []

        for flashcard in flashcards:
            result.append(self._map_flashcard(flashcard))
        return result

    async def get_count_in_deck(self, deck_id: FlashcardDeckId) -> int:
        session: AsyncSession = get_session()

        stmt = select(func.count()).where(FlashcardDB.flashcard_deck_id == deck_id.value)

        result = await session.execute(stmt)
        count = result.scalar_one()  # returns int

        return count

    async def _fetch_flashcards(
        self,
        deck_id: FlashcardDeckId,
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> List[FlashcardDB]:
        session: AsyncSession = get_session()

        stmt = select(FlashcardDB).where(FlashcardDB.flashcard_deck_id == deck_id.value)

        if search:
            stmt = stmt.where(FlashcardDB.front_word.ilike(f"%{search}%"))

        stmt = stmt.offset((page - 1) * per_page).limit(per_page)

        result = await session.execute(stmt)
        flashcards = result.scalars().all()  # Extract ORM objects

        return flashcards

    def _map_flashcard(self, fc: FlashcardDB) -> FlashcardRead:
        return FlashcardRead(
            id=FlashcardId(value=fc.id),
            front_word=fc.front_word,
            front_lang=Language.from_string(fc.front_lang),
            back_word=fc.back_word,
            back_lang=Language.from_string(fc.back_lang),
            front_context=fc.front_context,
            back_context=fc.back_context,
            general_rating=GeneralRating(value=GeneralRatingType.UNKNOWN),
            language_level=fc.language_level,
            rating_percentage=0.0,
            emoji=Emoji.from_unicode(fc.emoji) if fc.emoji else None,
            owner_type=FlashcardOwnerType.USER if fc.user_id else fc.admin_id,
        )
