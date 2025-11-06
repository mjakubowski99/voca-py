from src.flashcard.domain.models.story_flashcard import StoryFlashcard
from src.shared.value_objects.story_id import StoryId


from typing import List
from pydantic import BaseModel


class Story(BaseModel):
    id: StoryId
    flashcards: List[StoryFlashcard]
