from src.flashcard.application.services.iflashcard_selector import IFlashcardSelector
from src.flashcard.application.repository.contracts import ISessionRepository
from src.flashcard.application.repository.contracts import IFlashcardDeckRepository
from src.flashcard.domain.models.learning_session import LearningSession
from src.shared.enum import SessionStatus
from flashcard.application.command.create_session import CreateSession

from typing import Optional
from pydantic import BaseModel
from src.shared.enum import SessionType
from src.shared.value_objects.user_id import UserId
from flashcard.domain.value_objects import FlashcardDeckId, SessionId


class CreateSession(BaseModel):
    user_id: UserId
    cards_per_session: int
    device: str
    deck_id: Optional[FlashcardDeckId] = None
    type: SessionType

    class Config:
        frozen = True

    def has_deck_id(self) -> bool:
        return self.deck_id is not None

    def get_user_id(self) -> UserId:
        return self.user_id

    def get_cards_per_session(self) -> int:
        return self.cards_per_session

    def get_device(self) -> str:
        return self.device

    def get_deck_id(self) -> Optional[FlashcardDeckId]:
        return self.deck_id

    def get_type(self) -> SessionType:
        return self.type


class CreateSessionResultDTO(BaseModel):
    success: bool
    fail_reason: Optional[str] = None
    session_id: Optional[SessionId] = None

    class Config:
        frozen = True  # immutable like readonly in PHP

    def is_success(self) -> bool:
        return self.success

    def get_fail_reason(self) -> Optional[str]:
        return self.fail_reason

    def get_id(self) -> Optional[SessionId]:
        return self.session_id


class CreateSessionHandler:
    def __init__(
        self,
        repository: ISessionRepository,
        deck_repository: IFlashcardDeckRepository,
        selector: IFlashcardSelector,
    ):
        self.repository = repository
        self.deck_repository = deck_repository
        self.selector = selector

    async def handle(self, command: CreateSession) -> CreateSessionResultDTO:
        deck = None
        if command.has_deck_id():
            deck = await self.deck_repository.find_by_id(command.get_deck_id())

        await self.repository.set_all_owner_sessions_status(
            command.get_user_id(), SessionStatus.FINISHED
        )

        session = LearningSession.new_session(
            user_id=command.get_user_id(),
            type=command.get_type(),
            cards_per_session=command.get_cards_per_session(),
            device=command.get_device(),
            deck=deck,
        )

        session_id = await self.repository.create(session)

        await self.selector.reset_repetitions_in_session(command.get_user_id())

        return CreateSessionResultDTO(success=True, message=None, session_id=session_id)
