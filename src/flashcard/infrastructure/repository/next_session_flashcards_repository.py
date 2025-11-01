from typing import List
from sqlalchemy import select, func
from core.db import get_session
from src.flashcard.application.repository.contracts import INextSessionFlashcardsRepository
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import SessionId, FlashcardDeckId
from src.flashcard.domain.models.next_session_flashcards import NextSessionFlashcards
from src.flashcard.domain.models.deck import Deck
from src.shared.enum import SessionType, LanguageLevel
from core.models import LearningSessionFlashcards, FlashcardDecks
from src.flashcard.infrastructure.repository.session_repository import SessionRepository


class NotFoundException(Exception):
    pass


class NextSessionFlashcardsRepository(INextSessionFlashcardsRepository):
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def find(self, session_id: SessionId) -> NextSessionFlashcards:
        session_obj = await self.session_repo.find(session_id)
        session = get_session()  # Get AsyncSession instance

        # Counts query
        counts_stmt = (
            select(
                func.count(LearningSessionFlashcards.id).label("all_count"),
                func.count(func.nullif(LearningSessionFlashcards.rating, None)).label(
                    "unrated_count"
                ),
            )
            .where(LearningSessionFlashcards.learning_session_id == session_id.value)
            .where(LearningSessionFlashcards.is_additional == False)
        )
        counts_result = await session.execute(counts_stmt)
        counts_row = counts_result.first()
        all_count = counts_row.all_count if counts_row else 0
        unrated_count = counts_row.unrated_count if counts_row else 0

        # Deck query
        deck = None
        if session_obj.deck:
            deck_row = await session.get(FlashcardDecks, session_obj.deck.id.value)
            if deck_row:
                deck = Deck(
                    owner=session_obj.deck.owner,
                    tag=deck_row.tag,
                    name=deck_row.name,
                    default_language_level=LanguageLevel(deck_row.default_language_level),
                )
                deck.init(FlashcardDeckId(deck_row.id))

        return NextSessionFlashcards(
            session_id=session_id,
            session_type=SessionType(session_obj.type.value),
            user_id=UserId(session_obj.user_id.value),
            deck=deck,
            total_flashcards=all_count,
            unrated_flashcards=unrated_count,
            cards_per_session=session_obj.cards_per_session,
        )

    async def save(self, next_session_flashcards: NextSessionFlashcards) -> None:
        session = get_session()  # Get AsyncSession instance
        insert_data: List[LearningSessionFlashcards] = []

        for flashcard in (
            next_session_flashcards.get_next_flashcards()
            + next_session_flashcards.get_additional_flashcards()
        ):
            insert_data.append(
                LearningSessionFlashcards(
                    learning_session_id=next_session_flashcards.get_session_id().get_value(),
                    flashcard_id=flashcard.get_flashcard_id().get_value(),
                    rating=None,
                    is_additional=flashcard in next_session_flashcards.get_additional_flashcards(),
                    exercise_entry_id=flashcard.get_exercise_entry_id().get_value()
                    if flashcard.has_exercise()
                    else None,
                    exercise_type=flashcard.exercise_type.to_number()
                    if flashcard.has_exercise()
                    else None,
                )
            )
        session.add_all(insert_data)
        await session.commit()
