from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException
from src.flashcard.application.services.deck_resolver import DeckResolver
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.enum import LanguageLevel
from src.shared.user.iuser import IUser
from src.shared.value_objects.language import Language

from src.flashcard.application.services.flashcard_generator_service import FlashcardGeneratorService
from src.shared.value_objects.user_id import UserId


# DTO for the result
@dataclass(frozen=True)
class GenerateFlashcardsResult:
    deck_id: str
    flashcards_count: int
    existing_deck: bool


# Handler
class RegenerateFlashcardsHandler:
    def __init__(
        self, deck_resolver: DeckResolver, flashcard_generator_service: FlashcardGeneratorService
    ):
        self.deck_resolver = deck_resolver
        self.flashcard_generator_service = flashcard_generator_service

    async def handle(
        self,
        user: IUser,
        flashcard_deck_id: FlashcardDeckId,
        flashcards_limit: int,
        flashcards_save_limit: int,
    ) -> GenerateFlashcardsResult:
        resolved_deck = await self.deck_resolver.resolve_by_id(flashcard_deck_id.get_value())

        if (
            resolved_deck.deck.owner.is_user()
            and resolved_deck.deck.owner.id != user.get_id().get_value()
        ):
            raise HTTPException(
                status_code=403, detail="You are not allowed to regenerate flashcards for this deck"
            )

        flashcards_count = await self.flashcard_generator_service.generate(
            resolved_deck,
            user.get_user_language(),
            user.get_learning_language(),
            resolved_deck.deck.name,
            flashcards_limit,
            flashcards_save_limit,
        )

        return GenerateFlashcardsResult(
            deck_id=resolved_deck.deck.id,
            flashcards_count=flashcards_count,
            existing_deck=resolved_deck.is_existing_deck,
        )
