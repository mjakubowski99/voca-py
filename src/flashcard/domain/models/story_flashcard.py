from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.value_objects import StoryId

from pydantic import BaseModel
from typing import Optional

class StoryFlashcard(BaseModel):
    story_id: StoryId
    story_index: int
    sentence_override: Optional[str] = None
    flashcard: Flashcard