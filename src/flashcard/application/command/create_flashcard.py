from dataclasses import dataclass
from src.flashcard.application.repository.contracts import (
    IFlashcardDeckRepository,
    IFlashcardRepository,
)
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardId, FlashcardDeckId
from src.shared.enum import LanguageLevel
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId
from src.shared.models import Emoji


@dataclass(frozen=True)
class CreateFlashcard:
    user_id: UserId
    deck_id: FlashcardDeckId
    front_word: str
    back_word: str
    front_context: str
    back_context: str
    front_lang: Language
    back_lang: Language
    language_level: LanguageLevel
    emoji: str | None


@dataclass(frozen=True)
class CreateFlashcardResult:
    flashcard: Flashcard


class CreateFlashcardHandler:
    def __init__(
        self,
        deck_repository: IFlashcardDeckRepository,
        flashcard_repository: IFlashcardRepository,
    ):
        self.deck_repository = deck_repository
        self.flashcard_repository = flashcard_repository

    async def handle(self, command: CreateFlashcard) -> CreateFlashcardResult:
        # Get the deck to ensure it exists and get owner info
        deck = await self.deck_repository.find_by_id(command.deck_id)

        # Use the deck's owner to ensure consistency
        owner = deck.owner

        # Create emoji if provided
        emoji_obj = Emoji.from_unicode(command.emoji) if command.emoji else None

        # Create flashcard domain model
        flashcard = Flashcard(
            id=FlashcardId(value=0),  # Will be set by database
            front_word=command.front_word,
            front_lang=command.front_lang,
            back_word=command.back_word,
            back_lang=command.back_lang,
            front_context=command.front_context,
            back_context=command.back_context,
            owner=owner,
            deck=deck,
            level=command.language_level,
            emoji=emoji_obj,
        )

        # Save flashcard and get the created ID
        flashcard_id = await self.flashcard_repository.create(flashcard)

        # Update the flashcard with the generated ID
        flashcard.id = flashcard_id

        return CreateFlashcardResult(flashcard=flashcard)
