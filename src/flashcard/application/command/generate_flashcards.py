from dataclasses import dataclass
from typing import Any
from src.flashcard.application.services.deck_resolver import DeckResolver
from src.shared.value_objects.language import Language

from src.flashcard.application.services.flashcard_generator_service import FlashcardGeneratorService


# Command DTO
@dataclass(frozen=True)
class GenerateFlashcards:
    user_id: str
    front_lang: Language
    back_lang: Language
    deck_name: str
    language_level: str


# DTO for the result
@dataclass(frozen=True)
class GenerateFlashcardsResult:
    deck_id: str
    flashcards_count: int
    existing_deck: bool


# Handler
class GenerateFlashcardsHandler:
    def __init__(
        self, deck_resolver: DeckResolver, flashcard_generator_service: FlashcardGeneratorService
    ):
        self.deck_resolver = deck_resolver
        self.flashcard_generator_service = flashcard_generator_service

    async def handle(
        self,
        command: GenerateFlashcards,
        flashcards_limit: int,
        flashcards_save_limit: int,
    ) -> GenerateFlashcardsResult:
        # Resolve deck
        resolved_deck = await self.deck_resolver.resolve_by_name(
            command.user_id,
            command.front_lang.value,  # assuming Enum
            command.back_lang.value,
            command.deck_name,
            command.language_level,
        )

        # Generate flashcards
        flashcards_count = await self.flashcard_generator_service.generate(
            resolved_deck,
            command.front_lang,
            command.back_lang,
            command.deck_name,
            flashcards_limit,
            flashcards_save_limit,
        )

        return GenerateFlashcardsResult(
            deck_id=resolved_deck.deck.id,
            flashcards_count=flashcards_count,
            existing_deck=resolved_deck.is_existing_deck,
        )
