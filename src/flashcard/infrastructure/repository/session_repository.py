from typing import List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import SessionId
from src.flashcard.domain.models.learning_session import LearningSession
from src.shared.enum import SessionStatus
from src.flashcard.application.repository.contracts import ISessionRepository


class SessionRepository(ISessionRepository):
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
        return SessionId(session_obj.id)

    async def update(self, session_obj: LearningSession) -> None:
        session: AsyncSession = get_session()
        stmt = (
            update(LearningSession)
            .where(LearningSession.id == session_obj.id.value)
            .values(
                user_id=session_obj.user_id.value,
                status=session_obj.status.value,
                flashcard_deck_id=session_obj.deck.id.value if session_obj.deck else None,
                cards_per_session=session_obj.cards_per_session,
                device=session_obj.device,
            )
        )
        await session.execute(stmt)
        await session.commit()

    async def find(self, session_id: SessionId) -> LearningSession:
        session: AsyncSession = get_session()
        stmt = select(LearningSession).where(LearningSession.id == session_id.value)
        result = await session.execute(stmt)
        session_obj = result.scalar_one_or_none()
        if not session_obj:
            raise Exception("Session not found")
        return session_obj

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
