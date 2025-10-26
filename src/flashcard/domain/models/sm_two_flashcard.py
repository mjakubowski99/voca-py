from src.flashcard.domain.enum import Rating
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.user_id import UserId
from pydantic import BaseModel
from typing import Optional


class SmTwoFlashcard(BaseModel):
    INITIAL_REPETITION_RATIO: float = 2.5
    INITIAL_REPETITION_INTERVAL: float = 1.0

    user_id: UserId
    flashcard_id: FlashcardId
    repetition_ratio: float = INITIAL_REPETITION_RATIO
    repetition_interval: float = INITIAL_REPETITION_INTERVAL
    repetition_count: int = 0
    min_rating: int = 0
    repetitions_in_session: int = 0
    rating: Optional[Rating] = None

    def update_by_rating(self, rating: Rating) -> None:
        self.rating = rating

        if rating < self.min_rating:
            self.min_rating = rating

        self._calculate_repetition_interval(rating)
        self._calculate_repetition_ratio(rating)
        self.repetitions_in_session += 1

    def _calculate_repetition_interval(self, rating: Rating) -> None:
        if rating >= Rating.GOOD:
            if self.repetition_count == 0:
                self.repetition_interval = 1.0 if rating == Rating.GOOD else 6.0
            elif self.repetition_count == 1:
                self.repetition_interval = 6.0
            else:
                self.repetition_interval *= self.repetition_ratio
            self.repetition_count += 1
        else:
            self.repetition_interval = 1.0
            self.repetition_count = 0

    def _calculate_repetition_ratio(self, rating: Rating) -> None:
        adjustment = 0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02)
        self.repetition_ratio = round(self.repetition_ratio + adjustment, 6)
        if self.repetition_ratio < 1.3:
            self.repetition_ratio = 1.3