from typing import Optional
from shared.enum import SessionType, SessionStatus
from src.shared.value_objects.user_id import UserId
from flashcard.domain.value_objects import SessionId
from flashcard.domain.models.deck import Deck
from flashcard.domain.models.owner import Owner


class ForbiddenException(Exception):
    pass


class LearningSession:
    def __init__(
        self,
        status: SessionStatus,
        type_: SessionType,
        user_id: UserId,
        cards_per_session: int,
        device: str,
        deck: Optional[Deck] = None,
    ):
        self._id: Optional[SessionId] = None
        self.status = status
        self.type = type_
        self.user_id = user_id
        self.cards_per_session = cards_per_session
        self.device = device
        self.deck = deck

        self._validate()

    @classmethod
    def new_session(
        cls,
        user_id: UserId,
        type_: SessionType,
        cards_per_session: int,
        device: str,
        deck: Optional[Deck] = None,
    ) -> "Session":
        return cls(
            status=SessionStatus.STARTED,
            type_=type_,
            user_id=user_id,
            cards_per_session=cards_per_session,
            device=device,
            deck=deck,
        )

    def init(self, session_id: SessionId) -> "Session":
        self._id = session_id
        return self

    @property
    def id(self) -> SessionId:
        if self._id is None:
            raise ValueError("Session ID has not been initialized")
        return self._id

    @property
    def type(self) -> SessionType:
        return self.type

    @property
    def status(self) -> SessionStatus:
        return self.status

    @status.setter
    def status(self, value: SessionStatus):
        self.status = value

    @property
    def user_id(self) -> UserId:
        return self.user_id

    @property
    def cards_per_session(self) -> int:
        return self.cards_per_session

    @property
    def device(self) -> str:
        return self.device

    def has_flashcard_deck(self) -> bool:
        return self.deck is not None

    @property
    def get_deck(self) -> Optional[Deck]:
        return self.deck

    def _validate(self):
        if not self.has_flashcard_deck() or not self.deck.has_owner():
            return

        if self.deck.owner.is_admin():
            return

        is_owner = self.deck.owner.equals(Owner.from_user(self.user_id))
        if not is_owner:
            raise ForbiddenException("User is not authorized to create this deck")
