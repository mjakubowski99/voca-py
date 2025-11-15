from dataclasses import dataclass

from fastapi import HTTPException
from src.flashcard.application.repository.contracts import (
    IFlashcardDeckRepository,
    IFlashcardRepository,
)
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.value_objects import FlashcardId, FlashcardDeckId
from src.shared.enum import LanguageLevel
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId
from src.shared.models import Emoji


@dataclass(frozen=True)
class UpdateFlashcard:
    user_id: UserId
    flashcard_id: FlashcardId
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
class UpdateFlashcardResult:
    flashcard: Flashcard


class UpdateFlashcardHandler:
    def __init__(
        self,
        deck_repository: IFlashcardDeckRepository,
        flashcard_repository: IFlashcardRepository,
    ):
        self.deck_repository = deck_repository
        self.flashcard_repository = flashcard_repository

    async def handle(self, command: UpdateFlashcard) -> UpdateFlashcardResult:
        # Get the existing flashcard
        flashcards = await self.flashcard_repository.find_many([command.flashcard_id])
        if not flashcards:
            raise ValueError("Flashcard not found")

        existing_flashcard = flashcards[0]

        if (
            existing_flashcard.owner.is_user()
            and existing_flashcard.owner.id.value != command.user_id.value
        ):
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this flashcard"
            )

        deck = await self.deck_repository.find_by_id(command.deck_id)

        emoji_obj = Emoji.from_unicode(command.emoji) if command.emoji else None

        updated_flashcard = Flashcard(
            id=existing_flashcard.id,
            front_word=command.front_word,
            front_lang=command.front_lang,
            back_word=command.back_word,
            back_lang=command.back_lang,
            front_context=command.front_context,
            back_context=command.back_context,
            owner=existing_flashcard.owner,  # Keep the original owner
            deck=deck,
            level=command.language_level,
            emoji=emoji_obj,
            last_user_rating=existing_flashcard.last_user_rating,  # Keep the original rating
        )

        # Save updated flashcard
        await self.flashcard_repository.update(updated_flashcard)

        return UpdateFlashcardResult(flashcard=updated_flashcard)
