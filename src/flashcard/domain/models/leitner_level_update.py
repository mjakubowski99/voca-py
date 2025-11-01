from typing import List
from pydantic import BaseModel, Field
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import FlashcardId
from src.flashcard.domain.enum import Rating


class LeitnerLevelUpdate(BaseModel):
    user_id: UserId
    ids: List[FlashcardId] = Field(..., alias="flashcard_ids")
    leitner_level_increment_step: int

    class Config:
        frozen = True  # Makes the model immutable
        allow_population_by_field_name = True

    def increment_easy_ratings_count(self) -> bool:
        """
        Returns True if the Leitner level increment step is at or above the maximum Leitner level.
        """
        return self.leitner_level_increment_step >= Rating.max_leitner_level()
