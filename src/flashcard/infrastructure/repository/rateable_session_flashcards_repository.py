from typing import List
from sqlalchemy import select, update, case, func
from core.db import get_session
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import (
    SessionId,
    FlashcardId,
    FlashcardDeckId,
    SessionFlashcardId,
)
from src.flashcard.domain.models.rateable_session_flashcards import RateableSessionFlashcards
from src.flashcard.domain.models.rateable_session_flashcard import RateableSessionFlashcard
from src.shared.enum import SessionStatus
from core.models import LearningSessionFlashcards, LearningSessions  # ORM models
from src.flashcard.application.repository.contracts import IRateableSessionFlashcardsRepository


class RateableSessionFlashcardsRepository(IRateableSessionFlashcardsRepository):
    async def find(self, session_id: SessionId) -> RateableSessionFlashcards:
        session = get_session()

        # Fetch session info
        stmt_session = select(
            LearningSessions.id,
            LearningSessions.status,
            LearningSessions.user_id,
            LearningSessions.cards_per_session,
            LearningSessions.flashcard_deck_id,
        ).where(LearningSessions.id == session_id.value)
        session_result = await session.execute(stmt_session)
        session_row = session_result.first()

        if not session_row:
            raise Exception(f"Session {session_id.value} not found")

        stmt_rated_count = select(func.count(LearningSessionFlashcards.id)).where(
            LearningSessionFlashcards.learning_session_id == session_id.value,
            LearningSessionFlashcards.is_additional == False,
            LearningSessionFlashcards.rating.isnot(None),
        )
        rated_count_result = await session.execute(stmt_rated_count)
        rated_count = rated_count_result.scalar() or 0

        stmt_flashcards = select(
            LearningSessionFlashcards.id, LearningSessionFlashcards.flashcard_id
        ).where(
            LearningSessionFlashcards.learning_session_id == session_id.value,
            LearningSessionFlashcards.rating.is_(None),
        )
        flashcards_result = await session.execute(stmt_flashcards)
        flashcards_rows = flashcards_result.all()

        flashcards = [
            RateableSessionFlashcard(SessionFlashcardId(row.id), FlashcardId(row.flashcard_id))
            for row in flashcards_rows
        ]

        return RateableSessionFlashcards(
            session_id=SessionId(session_row.id),
            user_id=UserId(session_row.user_id),
            flashcard_deck_id=FlashcardDeckId(session_row.flashcard_deck_id)
            if session_row.flashcard_deck_id
            else None,
            status=SessionStatus(session_row.status),
            rated_count=rated_count,
            total_count=session_row.cards_per_session,
            rateable_session_flashcards=flashcards,
        )

    async def save(self, flashcards: RateableSessionFlashcards) -> None:
        session = get_session()

        # Update session status if changed
        stmt_status = (
            update(LearningSessions)
            .where(
                LearningSessions.id == flashcards.get_session_id().value,
                LearningSessions.status != flashcards.get_status().value,
            )
            .values(status=flashcards.get_status().value, updated_at=func.now())
        )
        await session.execute(stmt_status)

        # Update flashcard ratings
        rateable_flashcards = [f for f in flashcards.get_rateable_session_flashcards() if f.rated()]
        if not rateable_flashcards:
            return

        rating_case = case(
            {f.get_id().value: f.get_rating().value for f in rateable_flashcards},
            value=LearningSessionFlashcards.id,
        )
        stmt_update = (
            update(LearningSessionFlashcards)
            .where(
                LearningSessionFlashcards.learning_session_id == flashcards.get_session_id().value,
                LearningSessionFlashcards.id.in_([f.get_id().value for f in rateable_flashcards]),
            )
            .values(rating=rating_case, updated_at=func.now())
        )

        await session.execute(stmt_update)
        await session.commit()
