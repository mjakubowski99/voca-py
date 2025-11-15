from typing import List
from pydantic import BaseModel
from src.flashcard.domain.enum import Rating


class RatingStat(BaseModel):
    rating: Rating
    rating_percentage: float

    model_config = {"arbitrary_types_allowed": True}


class RatingStats(BaseModel):
    stats: List[RatingStat]

    model_config = {"arbitrary_types_allowed": True}
