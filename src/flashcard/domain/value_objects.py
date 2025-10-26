from src.shared.value_objects.integer_id import IntegerId

from uuid import UUID
from pydantic import BaseModel, field_validator


class OwnerId(BaseModel):
    value: UUID

    @field_validator("value", mode="before")
    def validate_uuid(cls, v):
        # Accept both string and UUID objects
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except ValueError:
            raise ValueError(f"Invalid UUID: {v}")

    @classmethod
    def from_string(cls, value: str) -> "OwnerId":
        return cls(value=value)

    def get_value(self) -> str:
        return str(self.value)

    def equals(self, other: object) -> bool:
        return isinstance(other, OwnerId) and self.value == other.value

    def __str__(self) -> str:
        return str(self.value)


class FlashcardId(IntegerId):
    pass


class FlashcardDeckId(IntegerId):
    pass


class SessionId(IntegerId):
    pass


class SessionFlashcardId(IntegerId):
    pass


class StoryId(IntegerId):
    pass
