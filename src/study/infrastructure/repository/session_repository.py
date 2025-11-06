from typing import List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import insert
from core.db import get_session
from core.models import LearningSessionFlashcards, LearningSessions
from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import FlashcardId, SessionId
from src.study.domain.enum import ExerciseType, SessionType
from src.study.domain.models.learning_session import LearningSession
from src.shared.enum import SessionStatus
from src.flashcard.application.repository.contracts import ISessionRepository
from src.study.domain.value_objects import LearningSessionId, LearningSessionStepId
from src.study.infrastructure.repository.unscramble_word_exercise_repository import (
    UnscrambleWordExerciseRepository,
)


class SessionRepository(ISessionRepository):
    def __init__(
        self,
        unscramble_repository: UnscrambleWordExerciseRepository,
        flashcard_facade: IFlashcardFacade,
    ):
        self.unscramble_repository = unscramble_repository
        self.flashcard_facade = flashcard_facade

    async def update_status_by_id(
        self, session_ids: List[SessionId], status: SessionStatus
    ) -> None:
        session: AsyncSession = get_session()
        stmt = (
            update(LearningSession)
            .where(LearningSession.id.in_([s.value for s in session_ids]))
            .values(status=status.value)
        )
        await session.execute(stmt)
        await session.commit()

    async def set_all_owner_sessions_status(self, user_id: UserId, status: SessionStatus) -> None:
        session: AsyncSession = get_session()
        stmt = (
            update(LearningSession)
            .where(LearningSession.user_id == user_id.value)
            .values(status=status.value)
        )
        await session.execute(stmt)
        await session.commit()

    async def create(self, session_obj: LearningSession) -> SessionId:
        session: AsyncSession = get_session()
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        if session_obj.new_steps:
            insert_data = [
                {
                    "learning_session_id": session_obj.get_id().get_value(),
                    "flashcard_id": step.get_flashcard_id().get_value(),
                    "rating": None,
                    "exercise_type": step.type.to_exercise_type().to_number(),
                    "exercise_entry_id": step.exercise_entry_id,
                }
                for step in session_obj.new_steps
            ]

        stmt_insert = (
            insert(LearningSessionFlashcards)
            .values(insert_data)
            .returning(LearningSessionFlashcards.id)
        )
        result = await session.execute(stmt_insert)
        step_ids = result.all()

        for i, step in enumerate(session_obj.new_steps):
            step.id = LearningSessionStepId(value=step_ids[i])

        session_obj.id = SessionId(session_obj.id)
        return session

    async def update(self, session_obj: LearningSession) -> None:
        session: AsyncSession = get_session()

        stmt_update_session = (
            update(LearningSession)
            .where(LearningSession.id == session_obj.id.value)
            .values(
                user_id=session_obj.user_id.value,
                status=session_obj.status.value,
                flashcard_deck_id=(session_obj.deck.id.value if session_obj.deck else None),
                cards_per_session=session_obj.cards_per_session,
                device=session_obj.device,
            )
        )
        await session.execute(stmt_update_session)

        if session_obj.new_steps:
            insert_data = [
                {
                    "learning_session_id": session_obj.get_id().get_value(),
                    "flashcard_id": step.get_flashcard_id().get_value(),
                    "rating": None,
                    "exercise_type": step.type.to_exercise_type().to_number(),
                    "exercise_entry_id": step.exercise_entry_id,
                }
                for step in session_obj.new_steps
            ]

            stmt_insert = insert(LearningSessionFlashcards).values(insert_data)
            await session.execute(stmt_insert)

        await session.commit()

    async def find(self, session_id: SessionId) -> LearningSession:
        session: AsyncSession = get_session()
        stmt = select(LearningSessions).where(LearningSessions.id == session_id.value)
        result = await session.execute(stmt)
        session_obj = result.scalar_one_or_none()

        stmt = (
            select(func.count())
            .select_from(LearningSessionFlashcards)
            .where(LearningSessionFlashcards.learning_session_id == session_id.get_value())
            .where(LearningSessionFlashcards.rating.isnot(None))
            .where(LearningSessionFlashcards.is_additional is False)
        )
        result = await session.execute(stmt)
        count = result.scalar_one()

        if not session_obj:
            raise Exception("Session not found")

        session = LearningSession(
            id=LearningSessionId(value=session_obj.id),
            status=SessionStatus(value=session_obj.status),
            type=SessionType(value=session_obj.type),
            progress=count,
            limit=session_obj.cards_per_session,
        )

        stmt = (
            select(LearningSessionFlashcards)
            .select_from(LearningSessionFlashcards)
            .where(LearningSessionFlashcards.learning_session_id == session_id.get_value())
            .where(LearningSessionFlashcards.rating is None)
            .where(LearningSessionFlashcards.is_additional is False)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for row in rows:
            if row.exercise_type is None:
                session.add_flashcard(
                    LearningSessionStepId(value=row.id),
                    await self.flashcard_facade.get_flashcard(FlashcardId(value=row.flashcard_id)),
                )
            if row.exercise_type == ExerciseType.UNSCRAMBLE_WORDS.to_number():
                session.add_unscramble_word_exercise(
                    LearningSessionStepId(value=row.id),
                    await self.unscramble_repository.find_by_entry_id(row.exercise_entry_id),
                )

        return session

    async def delete_all_for_user(self, user_id: UserId) -> None:
        session: AsyncSession = get_session()
        stmt = delete(LearningSession).where(LearningSession.user_id == user_id.value)
        await session.execute(stmt)
        await session.commit()

    async def has_any_session(self, user_id: UserId) -> bool:
        session: AsyncSession = get_session()
        stmt = select(func.count(LearningSession.id)).where(
            LearningSession.user_id == user_id.value
        )
        result = await session.execute(stmt)
        count = result.scalar()
        return count > 0
