from pydantic import BaseModel, Field, constr, conint
from src.flashcard.application.command.generate_flashcards import (
    GenerateFlashcards as GenerateFlashcardsCommand,
)
from src.flashcard.application.command.create_flashcard import (
    CreateFlashcard as CreateFlashcardCommand,
)
from src.flashcard.application.command.update_flashcard import (
    UpdateFlashcard as UpdateFlashcardCommand,
)
from src.flashcard.application.command.bulk_delete_flashcards import (
    BulkDeleteFlashcards as BulkDeleteFlashcardsCommand,
)
from src.shared.enum import LanguageLevel
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from typing import Optional, List


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


class CreateFlashcardRequest(BaseModel):
    flashcard_deck_id: int = Field(..., description="ID of the flashcard deck")
    front_word: str = Field(..., description="Word on the front of flashcard", example="Jabłko")
    back_word: str = Field(..., description="Word on the back of flashcard", example="Apple")
    front_context: str = Field(
        ..., description="Context sentence for the front word", example="Adam je jabłko"
    )
    back_context: str = Field(
        ..., description="Context sentence for the back word", example="Adam eats apple"
    )
    language_level: LanguageLevel = Field(
        ..., description="Language proficiency level", example="C1"
    )
    emoji: Optional[str] = Field(None, description="Emoji for the flashcard", example="❤️")

    def to_command(
        self,
        user_id: UserId,
        user_language: Language,
        learning_language: Language,
    ) -> CreateFlashcardCommand:
        """
        Convert request into application command.
        """
        return CreateFlashcardCommand(
            user_id=user_id,
            deck_id=FlashcardDeckId(value=self.flashcard_deck_id),
            front_word=self.front_word,
            back_word=self.back_word,
            front_context=self.front_context,
            back_context=self.back_context,
            front_lang=user_language,
            back_lang=learning_language,
            language_level=self.language_level,
            emoji=self.emoji,
        )


class UpdateFlashcardRequest(BaseModel):
    flashcard_deck_id: int = Field(..., description="ID of the flashcard deck")
    front_word: str = Field(..., description="Word on the front of flashcard", example="Jabłko")
    back_word: str = Field(..., description="Word on the back of flashcard", example="Apple")
    front_context: str = Field(
        ..., description="Context sentence for the front word", example="Adam je jabłko"
    )
    back_context: str = Field(
        ..., description="Context sentence for the back word", example="Adam eats apple"
    )
    language_level: LanguageLevel = Field(
        ..., description="Language proficiency level", example="C1"
    )
    emoji: Optional[str] = Field(None, description="Emoji for the flashcard", example="❤️")

    def to_command(
        self,
        user_id: UserId,
        flashcard_id: int,
        user_language: Language,
        learning_language: Language,
    ) -> UpdateFlashcardCommand:
        """
        Convert request into application command.
        """
        from src.flashcard.domain.value_objects import FlashcardId

        return UpdateFlashcardCommand(
            user_id=user_id,
            flashcard_id=FlashcardId(value=flashcard_id),
            deck_id=FlashcardDeckId(value=self.flashcard_deck_id),
            front_word=self.front_word,
            back_word=self.back_word,
            front_context=self.front_context,
            back_context=self.back_context,
            front_lang=user_language,
            back_lang=learning_language,
            language_level=self.language_level,
            emoji=self.emoji,
        )


class BulkDeleteFlashcardsRequest(BaseModel):
    flashcard_ids: List[int] = Field(
        ..., description="List of flashcard IDs to delete", example=[1, 2]
    )

    def to_command(self, user_id: UserId) -> BulkDeleteFlashcardsCommand:
        """
        Convert request into application command.
        """
        from src.flashcard.domain.value_objects import FlashcardId

        return BulkDeleteFlashcardsCommand(
            user_id=user_id,
            flashcard_ids=[FlashcardId(value=id) for id in self.flashcard_ids],
        )
