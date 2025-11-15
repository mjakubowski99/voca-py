from src.flashcard.domain.models.flashcard import Flashcard
from src.shared.flashcard.contracts import IFlashcardGroupItem
from src.shared.value_objects.story_id import StoryId

from pydantic import BaseModel
from typing import Optional


class StoryFlashcard(BaseModel, IFlashcardGroupItem):
    story_id: StoryId
    story_index: int
    sentence_override: Optional[str] = None
    flashcard: Flashcard

    def get_story_id(self) -> StoryId:
        return self.story_id

    def get_index(self) -> int:
        return self.story_index

    def get_flashcard(self) -> Flashcard:
        return self.flashcard
