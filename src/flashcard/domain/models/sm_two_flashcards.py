from src.flashcard.domain.enum import Rating
from src.flashcard.domain.models.sm_two_flashcard import SmTwoFlashcard
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.user_id import UserId
from pydantic import BaseModel, model_validator
from typing import List, Optional


class InvalidSmTwoFlashcardSetException(Exception):
    pass


class SmTwoFlashcards(BaseModel):
    sm_two_flashcards: List[SmTwoFlashcard]

    @model_validator(mode="after")
    def validate_set(self) -> "SmTwoFlashcards":
        if len(self.sm_two_flashcards) == 0:
            return self

        first_user_id = self.sm_two_flashcards[0].user_id
        for flashcard in self.sm_two_flashcards:
            if not flashcard.user_id.equals(first_user_id):
                raise InvalidSmTwoFlashcardSetException(
                    "Not every flashcard in set has same user id"
                )
        return self

    def fill_if_missing(self, user_id: UserId, flashcard_id: FlashcardId):
        if self._search_key_by_user_flashcard(flashcard_id) is None:
            self.sm_two_flashcards.append(
                SmTwoFlashcard(user_id=user_id, flashcard_id=flashcard_id)
            )

    def all(self) -> List[SmTwoFlashcard]:
        return self.sm_two_flashcards

    def update_by_rating(self, flashcard_id: FlashcardId, rating: Rating):
        key = self._search_key_by_user_flashcard(flashcard_id)
        if key is not None:
            self.sm_two_flashcards[key].update_by_rating(rating)

    def _search_key_by_user_flashcard(self, flashcard_id: FlashcardId) -> Optional[int]:
        for index, flashcard in enumerate(self.sm_two_flashcards):
            if flashcard.flashcard_id.equals(flashcard_id):
                return index
        return None

    def count(self) -> int:
        return len(self.sm_two_flashcards)
