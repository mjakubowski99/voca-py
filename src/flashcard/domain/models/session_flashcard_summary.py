from typing import Optional
from src.shared.flashcard.contracts import ISessionFlashcardSummary
from src.shared.models import Emoji
from src.shared.value_objects.language import Language
from flashcard.domain.models.flashcard import Flashcard


class SessionFlashcardSummary(ISessionFlashcardSummary):
    def __init__(
        self,
        order: int,
        flashcard: Flashcard,
        is_additional: bool,
        is_story_part: bool,
        story_sentence: Optional[str] = None,
    ):
        self._order = order
        self._flashcard = flashcard
        self._is_additional = is_additional
        self._is_story_part = is_story_part
        self._story_sentence = story_sentence

    def get_order(self) -> int:
        return self._order

    def get_flashcard(self) -> Flashcard:
        return self._flashcard

    def get_flashcard_id(self) -> int:
        return self._flashcard.get_id().value

    def get_front_word(self) -> str:
        return self._flashcard.get_front_word()

    def get_back_word(self) -> str:
        return self._flashcard.get_back_word()

    def get_front_context(self) -> str:
        return self._flashcard.get_front_context()

    def get_back_context(self) -> str:
        return self._flashcard.get_back_context()

    def get_front_lang(self) -> Language:
        return self._flashcard.get_front_lang()

    def get_back_lang(self) -> Language:
        return self._flashcard.get_back_lang()

    def get_emoji(self) -> Optional[Emoji]:
        return self._flashcard.get_emoji()

    def get_is_additional(self) -> bool:
        return self._is_additional

    def get_is_story_part(self) -> bool:
        return self._is_story_part

    def get_story_sentence(self) -> Optional[str]:
        return self._story_sentence
