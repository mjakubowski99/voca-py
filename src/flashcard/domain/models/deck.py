from typing import Generator, List, Optional
from pydantic import BaseModel, field_validator, validator, root_validator
import hashlib
from uuid import UUID
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import (
    FlashcardId,
    OwnerId,
    FlashcardDeckId,
    StoryId,
)
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId
from enum import Enum
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
