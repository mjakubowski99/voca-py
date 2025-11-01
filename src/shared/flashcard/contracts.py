from abc import ABC, abstractmethod
from src.shared.models import Emoji
from src.shared.value_objects.language import Language
from typing import List, Optional

from src.shared.value_objects.story_id import StoryId


class IAnswerOption(ABC):
    @abstractmethod
    def getOption() -> str:
        pass


class ISessionFlashcardSummary(ABC):
    @abstractmethod
    def get_flashcard_id(self) -> int:
        pass

    @abstractmethod
    def get_front_word(self) -> str:
        pass

    @abstractmethod
    def get_back_word(self) -> str:
        pass

    @abstractmethod
    def get_front_context(self) -> str:
        pass

    @abstractmethod
    def get_back_context(self) -> str:
        pass

    @abstractmethod
    def get_front_lang(self) -> Language:
        pass

    @abstractmethod
    def get_back_lang(self) -> Language:
        pass

    @abstractmethod
    def get_emoji(self) -> Optional[Emoji]:
        pass

    @abstractmethod
    def get_is_story_part(self) -> bool:
        pass

    @abstractmethod
    def get_story_sentence(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_order(self) -> int:
        pass


class ISessionFlashcardSummaries(ABC):
    @abstractmethod
    def has_story(self) -> bool:
        """Returns True if a story is associated with this set of summaries."""
        pass

    @abstractmethod
    def get_story_id(self) -> Optional[StoryId]:
        """Returns the story ID, or None if no story is associated."""
        pass

    @abstractmethod
    def get_summaries(self) -> List[ISessionFlashcardSummary]:
        """Returns a list of flashcard summaries."""
        pass

    @abstractmethod
    def get_answer_options(self) -> List[IAnswerOption]:
        """Returns a list of answer options."""
        pass
