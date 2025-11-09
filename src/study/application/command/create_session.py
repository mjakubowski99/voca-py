from typing import Optional
from pydantic import BaseModel, Field
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from src.shared.value_objects.user_id import UserId
from src.study.application.repository.contracts import ISessionRepository
from src.study.domain.enum import SessionType
from src.study.domain.models.learning_session import LearningSession


class CreateSession(BaseModel):
    user_id: UserId = Field(..., description="User ID")
    session_type: SessionType = Field(..., description="Session type")
    deck_id: Optional[FlashcardDeckId] = Field(..., description="Flashcard deck ID")
    limit: int = Field(..., description="Limit")
    device: str = Field(..., description="Device")

    class Config:
        use_enum_values = True
        frozen = True


class CreateSessionHandler:
    def __init__(self, repository: ISessionRepository):
        self.repository = repository

    async def handle(self, command: CreateSession) -> LearningSession:
        await self.repository.mark_all_user_sessions_finished(command.user_id)

        session = LearningSession.new_session(
            user_id=command.user_id,
            deck_id=command.deck_id,
            limit=command.limit,
            session_type=command.session_type,
            device=command.device,
        )

        return await self.repository.create(session)
