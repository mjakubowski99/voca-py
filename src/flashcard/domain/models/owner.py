from typing import Generator, List, Optional
from pydantic import BaseModel, field_validator, validator, root_validator
import hashlib
from uuid import UUID
from src.flashcard.domain.value_objects import FlashcardId, OwnerId, FlashcardDeckId, StoryId
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId
from enum import Enum
from src.shared.enum import LanguageLevel
from src.flashcard.domain.enum import FlashcardOwnerType


class Owner(BaseModel):
    id: OwnerId
    flashcard_owner_type: FlashcardOwnerType

    @classmethod
    def from_user(cls, user_id: UserId) -> "Owner":
        owner_id = OwnerId.from_string(str(user_id.value))
        return cls(id=owner_id, flashcard_owner_type=FlashcardOwnerType.USER)

    def equals(self, owner: "Owner") -> bool:
        return (
            self.id.equals(owner.get_id()) and self.flashcard_owner_type == owner.get_owner_type()
        )

    def is_user(self) -> bool:
        return self.flashcard_owner_type == FlashcardOwnerType.USER

    def is_admin(self) -> bool:
        return self.flashcard_owner_type == FlashcardOwnerType.ADMIN
