from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.domain.enum import FlashcardOwnerType
from src.shared.enum import LanguageLevel


class OwnerDeckRead(BaseModel):
    id: FlashcardDeckId = Field(..., description="Unique identifier of the flashcard deck")
    name: str = Field(..., description="Deck name")
    language_level: LanguageLevel = Field(
        ..., description="Detected or default language level of the deck"
    )
    flashcards_count: int = Field(..., description="Total number of flashcards in the deck")
    rating_percentage: float = Field(
        ..., description="Average rating percentage across all flashcards"
    )
    last_learnt_at: Optional[datetime] = Field(
        None, description="Timestamp of the last learning session for this deck"
    )
    owner_type: FlashcardOwnerType = Field(..., description="Type of deck owner (USER or ADMIN)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": {"value": 123},
                "name": "Basic Spanish Vocabulary",
                "language_level": "A2",
                "flashcards_count": 120,
                "rating_percentage": 82.5,
                "last_learnt_at": "2025-10-25T14:30:00Z",
                "owner_type": "USER",
            }
        }
        use_enum_values = True
        arbitrary_types_allowed = True
