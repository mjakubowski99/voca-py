from typing import List, Optional
from src.shared.flashcard.contracts import IFlashcard, IFlashcardGroup, IFlashcardGroupItem
from src.shared.value_objects.story_id import StoryId
from pydantic import BaseModel


class FlashcardGroupItem(BaseModel, IFlashcardGroupItem):
    story_id: Optional[StoryId] = None
    index: int
    flashcard: IFlashcard

    def get_story_id(self) -> Optional[StoryId]:
        return self.story_id

    def get_index(self) -> int:
        return self.index

    def get_flashcard(self) -> IFlashcard:
        return self.flashcard

    model_config = {
        "arbitrary_types_allowed": True,
    }


class FlashcardGroup(BaseModel, IFlashcardGroup):
    story_id: Optional[StoryId] = None
    flashcards: List[IFlashcardGroupItem]

    def get_story_id(self) -> Optional[StoryId]:
        return self.story_id

    def get_flashcards(self) -> List[IFlashcardGroupItem]:
        return self.flashcards

    model_config = {
        "arbitrary_types_allowed": True,
    }
