from typing import Optional
from pydantic import BaseModel
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from src.shared.flashcard.contracts import IPickingContext
from src.shared.user.iuser import IUser


class PickingContext(BaseModel, IPickingContext):
    user: IUser
    deck_id: Optional[FlashcardDeckId]
    max_flashcards_count: int
    current_count: int

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def get_user(self) -> IUser:
        return self.user

    def get_flashcard_deck_id(self) -> Optional[FlashcardDeckId]:
        return self.deck_id

    def get_max_flashcards_count(self) -> int:
        return self.max_flashcards_count

    def get_current_count(self) -> int:
        return self.current_count
