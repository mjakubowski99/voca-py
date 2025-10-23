from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4


class UserId(BaseModel):
    value: UUID = Field(..., description="Unique user identifier")

    class Config:
        frozen = True  # Makes the model immutable like a value object
        allow_mutation = False
        json_encoders = {UUID: str}  # Serialize UUIDs as strings

    @classmethod
    def new(cls) -> "UserId":
        """Generate a new random UserId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "UserId":
        """Create a UserId from a string UUID."""
        return cls(value=value)

    def get_value(self) -> str:
        """Return the UUID as a string."""
        return str(self.value)

    def equals(self, other: object) -> bool:
        """Compare two UserId instances for equality."""
        return isinstance(other, UserId) and self.value == other.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"UserId({self.value})"
