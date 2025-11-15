from src.flashcard.domain.models.story_flashcard import StoryFlashcard
from src.shared.flashcard.contracts import IFlashcardGroup
from src.shared.value_objects.story_id import StoryId


from typing import List
from pydantic import BaseModel


class Story(BaseModel, IFlashcardGroup):
    id: StoryId
    flashcards: List[StoryFlashcard]

    def get_story_id(self) -> StoryId:
        return self.id

    def get_flashcards(self) -> List[StoryFlashcard]:
        return self.flashcards
