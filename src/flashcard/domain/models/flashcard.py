from src.flashcard.domain.enum import FlashcardOwnerType, Rating
from src.flashcard.domain.models.deck import Deck
from src.shared.flashcard.contracts import IFlashcard
from src.shared.models import Emoji
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.flashcard_id import FlashcardId as SharedFlashcardId
from src.shared.enum import LanguageLevel
from src.shared.value_objects.language import Language
from pydantic import BaseModel, root_validator
from typing import Optional

import hashlib


class Flashcard(BaseModel, IFlashcard):
    id: FlashcardId
    front_word: str
    front_lang: Language
    back_word: str
    back_lang: Language
    front_context: str
    back_context: str
    owner: Optional[Owner] = None
    deck: Optional[Deck] = None
    level: LanguageLevel
    emoji: Optional[Emoji] = None
    last_user_rating: Optional[Rating] = None
    learned_language: Language = None  # will be set in validation

    @root_validator(pre=True)
    def set_learned_language_and_validate_level(cls, values):
        back_lang = values.get("back_lang")
        level = values.get("level")
        if back_lang is None or level is None:
            raise ValueError("back_lang and level must be provided")

        values["learned_language"] = Language(value=back_lang.get_value())

        # Validate level
        if level not in values["learned_language"].get_available_levels():
            raise ValueError(
                f"Invalid language level: {level} for language {values['learned_language'].value}"
            )
        return values

    def has_owner(self) -> bool:
        return self.owner is not None

    def has_deck(self) -> bool:
        return self.deck is not None

    def hash(self) -> str:
        combined = (
            self.front_word
            + self.front_lang.value
            + self.back_word
            + self.back_lang.value
            + self.front_context
            + self.back_context
        )
        return hashlib.md5(combined.encode("utf-8")).hexdigest()

    class Config:
        arbitrary_types_allowed = True

    def get_flashcard_id(self) -> SharedFlashcardId:
        return SharedFlashcardId(value=self.id.get_value())

    def get_front_word(self) -> str:
        return self.front_word

    def get_back_word(self) -> str:
        return self.back_word

    def get_front_context(self) -> str:
        return self.front_context

    def get_back_context(self) -> str:
        return self.back_context

    def get_front_lang(self) -> Language:
        return self.front_lang

    def get_back_lang(self) -> Language:
        return self.back_lang

    def get_emoji(self) -> Optional[Emoji]:
        return self.emoji

    def get_owner_type(self) -> FlashcardOwnerType:
        return self.owner.flashcard_owner_type
