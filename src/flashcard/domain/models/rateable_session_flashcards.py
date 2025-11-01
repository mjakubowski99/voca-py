from typing import List, Optional
from src.shared.enum import SessionStatus
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import (
    SessionId,
    FlashcardId,
    FlashcardDeckId,
    SessionFlashcardId,
)
from src.flashcard.domain.enum import Rating
from src.flashcard.domain.models.session_flashcards_base import SessionFlashcardsBase
from src.flashcard.domain.models.rateable_session_flashcard import RateableSessionFlashcard


class SessionFinishedException(Exception):
    pass


class RateableSessionFlashcardNotFound(Exception):
    pass


class RateableSessionFlashcards(SessionFlashcardsBase):
    def __init__(
        self,
        session_id: SessionId,
        user_id: UserId,
        flashcard_deck_id: Optional[FlashcardDeckId],
        status: SessionStatus,
        rated_count: int,
        total_count: int,
        rateable_session_flashcards: List[RateableSessionFlashcard],
    ):
        if status == SessionStatus.FINISHED:
            raise SessionFinishedException("Session already finished")

        self.session_id = session_id
        self.user_id = user_id
        self.flashcard_deck_id = flashcard_deck_id
        self.status = status
        self.rated_count = rated_count
        self.total_count = total_count
        self.rateable_session_flashcards = rateable_session_flashcards

    def get_rateable_session_flashcards(self) -> List[RateableSessionFlashcard]:
        return self.rateable_session_flashcards

    def has_deck(self) -> bool:
        return self.flashcard_deck_id is not None

    def get_deck_id(self) -> FlashcardDeckId:
        return self.flashcard_deck_id

    def all(self) -> List[RateableSessionFlashcard]:
        return self.rateable_session_flashcards

    def get_session_id(self) -> SessionId:
        return self.session_id

    def get_session_user_id(self) -> UserId:
        return self.user_id

    def get_user_id_for_flashcard(self, _id: SessionFlashcardId) -> UserId:
        return self.user_id

    def get_status(self) -> SessionStatus:
        return self.status

    def is_empty(self) -> bool:
        return len(self.rateable_session_flashcards) == 0

    def rate(self, session_flashcard_id: SessionFlashcardId, rating: Rating) -> None:
        key = self._find_key_by_id(session_flashcard_id)
        self.rateable_session_flashcards[key].rate(rating)
        self.rated_count += 1

        if self.rated_count >= self.total_count:
            self.status = SessionStatus.FINISHED

    def _find_key_by_id(self, session_flashcard_id: SessionFlashcardId) -> int:
        for idx, flashcard in enumerate(self.rateable_session_flashcards):
            if flashcard.get_id() == session_flashcard_id:
                return idx
        raise RateableSessionFlashcardNotFound(
            f"Flashcard already rated or does not exist: {session_flashcard_id}"
        )

    def get_rated_session_flashcard_ids(self) -> List[SessionFlashcardId]:
        return [f.get_id() for f in self.rateable_session_flashcards if f.rated()]

    def get_flashcard_rating(self, session_flashcard_id: SessionFlashcardId) -> Rating:
        for flashcard in self.rateable_session_flashcards:
            if flashcard.get_id() == session_flashcard_id:
                return flashcard.get_rating()
        raise RateableSessionFlashcardNotFound(f"Flashcard not found: {session_flashcard_id}")

    def get_flashcard_id(self, session_flashcard_id: SessionFlashcardId) -> FlashcardId:
        for flashcard in self.rateable_session_flashcards:
            if flashcard.get_id() == session_flashcard_id:
                return flashcard.get_flashcard_id()
        raise RateableSessionFlashcardNotFound(f"Flashcard not found: {session_flashcard_id}")

    def update_poll(self, session_flashcard_id: SessionFlashcardId) -> bool:
        return self.has_flashcard_poll()
