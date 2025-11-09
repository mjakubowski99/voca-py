from typing import Optional
from pydantic import BaseModel
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.enum import LanguageLevel


class Deck(BaseModel):
    owner: Owner
    tag: str
    name: str
    default_language_level: LanguageLevel
    id: Optional[FlashcardDeckId] = None  # Will be set using init()

    def init(self, deck_id: FlashcardDeckId) -> "Deck":
        self.id = deck_id
        return self

    def get_id(self) -> Optional[FlashcardDeckId]:
        return self.id

    def has_owner(self) -> bool:
        return True

    def set_name(self, name: str) -> None:
        self.name = name
