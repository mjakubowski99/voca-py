from datetime import datetime
from pydantic import BaseModel, Field
from src.shared.enum import Language, LanguageLevel
from src.flashcard.domain.enum import GeneralRatingType, FlashcardOwnerType, Rating
from typing import List, Optional


class OwnerDeckItem(BaseModel):
    id: int = Field(..., description="Deck id")
    name: str = Field(..., description="Deck name")
    language_level: LanguageLevel = Field(..., description="Detected or default language level")
    flashcards_count: int = Field(..., description="Count of flashcards in this deck")
    rating_percentage: float = Field(..., description="Average rating percentage")
    last_learnt_at: datetime | None = Field(None, description="Last learning session timestamp")
    owner_type: FlashcardOwnerType = Field(..., description="Deck owner type (USER or ADMIN)")


class FlashcardDecksResource(BaseModel):
    decks: List[OwnerDeckItem] = Field(
        ..., description="List of flashcard decks belonging to the user or admin"
    )
    page: int = Field(..., description="Current page number", example=1)
    per_page: int = Field(..., description="Number of decks per page", example=15)

    class Config:
        json_schema_extra = {
            "example": {
                "decks": [
                    {
                        "id": {"value": 11},
                        "name": "Two people talk",
                        "language_level": "A2",
                        "flashcards_count": 1,
                        "last_learnt_at": "2025-10-25T14:30:00Z",
                        "rating_percentage": 66.66,
                        "owner_type": "USER",
                    }
                ],
                "page": 1,
                "per_page": 15,
            }
        }


class FlashcardResponse(BaseModel):
    id: int = Field(..., description="Flashcard ID", example=11)
    front_word: str = Field(..., description="Word on the front of flashcard", example="Polish")
    front_lang: Language = Field(..., description="Language of the front word", example=Language.EN)
    back_word: str = Field(..., description="Word on the back of flashcard", example="Polska")
    back_lang: Language = Field(..., description="Language of the back word", example=Language.PL)
    front_context: str = Field(
        ...,
        description="Context sentence for the word on front of flashcard",
        example="Country in the center of Europe",
    )
    back_context: str = Field(
        ...,
        description="Context sentence for the word on back of flashcard",
        example="Kraj w centrum Europy",
    )
    rating: GeneralRatingType = Field(
        ..., description="General rating of flashcard", example=GeneralRatingType.NEW
    )
    language_level: Optional[LanguageLevel] = Field(
        None, description="Language level", example=LanguageLevel.C1
    )
    rating_percentage: float = Field(
        ..., description="How well user knows this flashcard", example=66.66
    )
    emoji: Optional[str] = Field(None, description="Flashcard context emoji", example="❤️")
    owner_type: FlashcardOwnerType = Field(..., description="Owner type of flashcard")


class DeckDetailsResponse(BaseModel):
    id: int = Field(..., description="ID of the session", example=10)
    name: str = Field(..., description="Category name", example="Two people talk")
    language_level: LanguageLevel = Field(..., description="Language level of deck")
    last_learnt_at: Optional[datetime] = Field(
        None, description="Timestamp of last learning of this deck"
    )
    rating_percentage: float = Field(
        ...,
        description="Rating percentage which tells how well user knows this deck",
        example=66.66,
    )
    owner_type: FlashcardOwnerType = Field(..., description="Owner type of deck")
    flashcards: List[FlashcardResponse] = Field(
        ..., description="List of flashcards in the session"
    )
    page: int = Field(..., description="Page number", example=1)
    per_page: int = Field(..., description="Items per page", example=15)
    flashcards_count: int = Field(..., description="Count of flashcards in deck", example=15)


class BulkDeleteFlashcardsResponse(BaseModel):
    deleted_count: int = Field(..., description="Number of flashcards deleted", example=2)


class RatingStat(BaseModel):
    rating: Rating = Field(..., description="Rating")
    rating_percentage: float = Field(..., description="Rating percentage")

    model_config = {"arbitrary_types_allowed": True}


class RatingStatsResponse(BaseModel):
    stats: List[RatingStat] = Field(..., description="List of rating stats")
