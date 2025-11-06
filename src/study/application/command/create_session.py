from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.value_objects.user_id import UserId
from src.study.application.repository.contracts import ISessionRepository
from src.study.domain.enum import SessionType
from src.study.domain.models.learning_session import LearningSession


class CreateSession:
    user_id: UserId
    session_type: SessionType
    flashcard_deck_id: FlashcardDeckId
    limit: int


class CreateSessionHandler:
    def __init__(self, repository: ISessionRepository):
        self.repository = repository

    async def handle(self, command: CreateSession):
        await self.repository.mark_all_user_sessions_finished(command.user_id)

        session = LearningSession.new_session(
            user_id=command.user_id,
            deck_id=command.flashcard_deck_id,
            limit=command.limit,
            type=command.session_type,
        )

        await self.repository.create(session)
