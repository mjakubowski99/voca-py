from typing import Optional
from pydantic import BaseModel
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.flashcard.contracts import IPickingContext
from src.shared.value_objects.user_id import UserId


class PickingContext(BaseModel, IPickingContext):
    user_id: UserId
    flashcard_deck_id: Optional[FlashcardDeckId]

    def get_user_id(self) -> UserId:
        return self.user_id

    def get_flashcard_deck_id(self) -> Optional[FlashcardDeckId]:
        return super().get_flashcard_deck_id()
