from typing import Optional
from src.flashcard.domain.value_objects import FlashcardId, SessionFlashcardId
from src.flashcard.domain.enum import Rating


class SessionFlashcardAlreadyRatedException(Exception):
    pass


class RateableSessionFlashcard:
    def __init__(self, id: SessionFlashcardId, flashcard_id: FlashcardId):
        self._id = id
        self._flashcard_id = flashcard_id
        self._rating: Optional[Rating] = None

    @property
    def id(self) -> SessionFlashcardId:
        return self._id

    @property
    def flashcard_id(self) -> FlashcardId:
        return self._flashcard_id

    def rated(self) -> bool:
        return self._rating is not None

    def get_rating(self) -> Optional[Rating]:
        return self._rating

    def rate(self, rating: Rating) -> None:
        if self.rated():
            raise SessionFlashcardAlreadyRatedException(f"Flashcard already rated: {self._id}")
        self._rating = rating
