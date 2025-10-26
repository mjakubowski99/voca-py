from typing import Optional, ClassVar
from pydantic import BaseModel
from src.flashcard.domain.enum import Rating, GeneralRatingType


# GeneralRating class
class GeneralRating(BaseModel):
    value: GeneralRatingType

    MAP: ClassVar[dict[Rating, GeneralRatingType]] = {
        Rating.GOOD: GeneralRatingType.GOOD,
        Rating.VERY_GOOD: GeneralRatingType.VERY_GOOD,
        Rating.UNKNOWN: GeneralRatingType.UNKNOWN,
        Rating.WEAK: GeneralRatingType.WEAK,
    }

    @classmethod
    def from_value(cls, value: Optional[int]) -> "GeneralRating":
        if value is None:
            return cls(value=GeneralRatingType.NEW)
        return cls(value=cls.MAP[value])

    def to_score(self) -> float:
        return {
            GeneralRatingType.NEW: 0.0,
            GeneralRatingType.WEAK: 25.0,
            GeneralRatingType.UNKNOWN: 50.0,
            GeneralRatingType.GOOD: 75.0,
            GeneralRatingType.VERY_GOOD: 100.0,
        }[self.value]
