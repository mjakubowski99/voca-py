from typing import List
from sqlalchemy import select, text, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import insert
from core.logging import logger
from core.models import LearningSessionFlashcards, LearningSessions
from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.value_objects.flashcard_id import FlashcardId
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from src.shared.value_objects.user_id import UserId
from src.study.domain.value_objects import LearningSessionId
from src.study.domain.enum import ExerciseType, Rating, SessionType
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.enum import SessionStatus
from src.study.application.repository.contracts import ISessionRepository
from src.study.domain.value_objects import ExerciseEntryId, LearningSessionStepId
from src.study.infrastructure.repository.unscramble_word_exercise_repository import (
    UnscrambleWordExerciseRepository,
)
from src.study.infrastructure.repository.word_match_exercise_repository import (
    WordMatchExerciseRepository,
)


class LearningSessionRepository(ISessionRepository):
    def __init__(
        self,
        unscramble_repository: UnscrambleWordExerciseRepository,
        word_match_repository: WordMatchExerciseRepository,
        flashcard_facade: IFlashcardFacade,
        session: AsyncSession,
    ):
        self.unscramble_repository = unscramble_repository
        self.word_match_repository = word_match_repository
        self.flashcard_facade = flashcard_facade
        self.session = session

    async def update_status_by_id(
        self, session_ids: List[LearningSessionId], status: SessionStatus
    ) -> None:
        stmt = (
            update(LearningSession)
            .where(LearningSession.id.in_([s.value for s in session_ids]))
            .values(status=status.value)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def set_all_owner_sessions_status(self, user_id: UserId, status: SessionStatus) -> None:
        stmt = (
            update(LearningSession)
            .where(LearningSession.user_id == user_id.value)
            .values(status=status.value)
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def create(self, session_obj: LearningSession) -> LearningSession:
        db_session = LearningSessions(
            user_id=session_obj.user_id.value,
            type=session_obj.type.value,
            status=session_obj.status.value,
            flashcard_deck_id=(session_obj.deck_id.value if session_obj.deck_id else None),
            cards_per_session=session_obj.limit,
            device=session_obj.device,
        )

        self.session.add(db_session)
        await self.session.commit()
        await self.session.refresh(db_session)
        session_obj.id = LearningSessionId(value=db_session.id)

        return session_obj

    async def save_new_steps(self, session_obj: LearningSession) -> None:
        if session_obj.new_steps:
            insert_data = [
                {
                    "learning_session_id": session_obj.id.get_value(),
                    "flashcard_id": step.get_flashcard_id().get_value(),
                    "rating": (step.rating.value if step.rating else None),
                    "exercise_type": (
                        step.get_exercise_type().to_number() if step.get_exercise_type() else None
                    ),
                    "exercise_entry_id": step.get_exercise_entry_id(),
                }
                for step in session_obj.new_steps
                if step.id.is_empty()
            ]

            if len(insert_data) == 0:
                return session_obj

            stmt_insert = (
                insert(LearningSessionFlashcards)
                .values(insert_data)
                .returning(LearningSessionFlashcards.id)
            )

            result = await self.session.execute(stmt_insert)
            inserted_ids = [row[0] for row in result.fetchall()]

        await self.session.commit()

        for index, inserted_id in enumerate(inserted_ids):
            session_obj.new_steps[index].id = LearningSessionStepId(value=inserted_id)

        return session_obj

    async def find(self, session_id: LearningSessionId) -> LearningSession:
        stmt = select(LearningSessions).where(LearningSessions.id == session_id.get_value())
        result = await self.session.execute(stmt)
        session_obj = result.scalar_one_or_none()

        stmt = (
            select(func.count())
            .where(LearningSessionFlashcards.learning_session_id == session_id.get_value())
            .where(LearningSessionFlashcards.rating.isnot(None))
            .where(LearningSessionFlashcards.is_additional.is_(False))
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one()

        if not session_obj:
            raise Exception("Session not found")

        learning_session = LearningSession(
            id=LearningSessionId(value=session_obj.id),
            user_id=UserId(value=session_obj.user_id),
            status=SessionStatus(value=session_obj.status),
            type=SessionType(value=session_obj.type),
            progress=count,
            limit=session_obj.cards_per_session,
            deck_id=FlashcardDeckId(value=session_obj.flashcard_deck_id)
            if session_obj.flashcard_deck_id
            else None,
            device=session_obj.device,
            new_steps=[],
        )

        stmt = (
            select(
                LearningSessionFlashcards.id,
                LearningSessionFlashcards.learning_session_id,
                LearningSessionFlashcards.exercise_type,
                LearningSessionFlashcards.exercise_entry_id,
                LearningSessionFlashcards.flashcard_id,
            )
            .where(LearningSessionFlashcards.learning_session_id == session_id.get_value())
            .where(LearningSessionFlashcards.rating.is_(None))
            .where(LearningSessionFlashcards.is_additional.is_(False))
        )
        result = await self.session.execute(stmt)
        rows = result.all()

        for row in rows:
            if row.exercise_type is None:
                learning_session.add_flashcard(
                    LearningSessionStepId(value=row.id),
                    await self.flashcard_facade.get_flashcard(FlashcardId(value=row.flashcard_id)),
                )
            if row.exercise_type == ExerciseType.UNSCRAMBLE_WORDS.to_number():
                learning_session.add_unscramble_exercise(
                    LearningSessionStepId(value=row.id),
                    await self.unscramble_repository.find_by_entry_id(
                        ExerciseEntryId(row.exercise_entry_id)
                    ),
                )
            if row.exercise_type == ExerciseType.WORD_MATCH.to_number():
                learning_session.add_word_match_exercise(
                    LearningSessionStepId(value=row.id),
                    await self.word_match_repository.find_by_entry_id(
                        ExerciseEntryId(row.exercise_entry_id)
                    ),
                )

        return learning_session

    async def delete_all_for_user(self, user_id: UserId) -> None:
        stmt = delete(LearningSessions).where(LearningSessions.user_id == user_id.value)
        await self.session.execute(stmt)
        await self.session.commit()

    async def has_any_session(self, user_id: UserId) -> bool:
        stmt = select(func.count(LearningSession.id)).where(
            LearningSession.user_id == user_id.value
        )
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def mark_all_user_sessions_finished(self, user_id: UserId) -> None:
        pass

    async def update_flashcard_rating(
        self, step_id: LearningSessionStepId, rating: Rating
    ) -> FlashcardId:
        stmt = (
            update(LearningSessionFlashcards)
            .where(LearningSessionFlashcards.id == step_id.value)
            .values(rating=rating.value)
        )

        await self.session.execute(stmt)

        stmt = select(LearningSessionFlashcards.flashcard_id).where(
            LearningSessionFlashcards.id == step_id.value
        )

        result = await self.session.execute(stmt)
        return FlashcardId(value=result.scalar_one())

    async def update_flashcard_rating_by_entry_id(
        self, entry_id: ExerciseEntryId, rating: Rating
    ) -> FlashcardId:
        stmt = (
            update(LearningSessionFlashcards)
            .where(LearningSessionFlashcards.exercise_entry_id == entry_id.value)
            .values(rating=rating.value)
        )

        await self.session.execute(stmt)
        await self.session.commit()
