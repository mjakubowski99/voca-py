from pydantic import BaseModel, Field, constr, conint
from src.flashcard.application.command.generate_flashcards import (
    GenerateFlashcards as GenerateFlashcardsCommand,
)
from src.shared.enum import LanguageLevel
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language
from typing import Optional


class GetUserDecksRequest(BaseModel):
    search: Optional[str] = Field(None, description="Optional search term to filter deck names")
    page: int = Field(1, ge=1, description="Page number for pagination, must be >= 1")
    per_page: int = Field(
        15, ge=1, le=100, description="Number of decks per page, between 1 and 100"
    )


class GetAdminDecksRequest(BaseModel):
    search: Optional[str] = Field(None, description="Optional search term to filter deck names")
    language_level: Optional[LanguageLevel] = Field(..., description="Language proficiency level")
    page: Optional[int] = Field(1, ge=1, description="Page number for pagination, must be >= 1")
    per_page: Optional[int] = Field(
        15, ge=1, le=100, description="Number of decks per page, between 1 and 100"
    )


class GenerateFlashcards(BaseModel):
    category_name: constr(min_length=5, max_length=40) = Field(
        ...,
        description="Category name provided by user",
        example="Two people talk",
    )
    language_level: LanguageLevel = Field(..., description="Language proficiency level")
    page: conint(ge=0) = Field(1, description="Page number (default: 1)")
    per_page: conint(ge=0, le=30) = Field(15, description="Items per page (default: 15)")

    def to_command(
        self,
        user_id: UserId,
        user_language: Language,
        learning_language: Language,
    ) -> GenerateFlashcardsCommand:
        """
        Convert request into application command.
        """
        return GenerateFlashcardsCommand(
            user_id=user_id,
            deck_name=self.category_name,
            language_level=self.language_level,
            front_lang=user_language,
            back_lang=learning_language,
        )
