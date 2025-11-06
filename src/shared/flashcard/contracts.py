from abc import ABC, abstractmethod
from typing import Optional

from src.flashcard.domain.value_objects import FlashcardDeckId, FlashcardId
from src.shared.models import Emoji
from src.shared.value_objects.language import Language
from src.shared.user.iuser import IUser
from src.study.domain.enum import Rating


class IRatingContext(ABC):
    @abstractmethod
    def get_user(self) -> IUser:
        pass

    @abstractmethod
    def get_flashcard_id(self) -> FlashcardId:
        pass

    @abstractmethod
    def get_rating(self) -> Rating:
        pass


class IPickingContext(ABC):
    """Kontekst używany przy wyborze fiszki."""

    @abstractmethod
    def get_user(self) -> IUser:
        """Zwraca identyfikator użytkownika."""
        pass

    @abstractmethod
    def get_flashcard_deck_id(self) -> Optional[FlashcardDeckId]:
        """Zwraca opcjonalne ID talii fiszek."""
        pass

    @abstractmethod
    def get_max_flashcards_count(self) -> int:
        """Zwraca opcjonalne ID talii fiszek."""
        pass

    @abstractmethod
    def get_current_count(self) -> int:
        """Zwraca opcjonalne ID talii fiszek."""
        pass


class IFlashcard(ABC):
    """Interfejs reprezentujący pojedynczą fiszkę."""

    @abstractmethod
    def get_flashcard_id(self) -> FlashcardId:
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


class IFlashcardFacade(ABC):
    """Interfejs fasady do zarządzania fiszkami."""

    @abstractmethod
    async def get_flashcard(self, id: FlashcardId) -> IFlashcard:
        """Wybiera odpowiednią fiszkę na podstawie kontekstu."""
        pass

    @abstractmethod
    async def pick_flashcard(self, context: IPickingContext) -> IFlashcard:
        """Wybiera odpowiednią fiszkę na podstawie kontekstu."""
        pass

    @abstractmethod
    async def new_rating(self, flashcard_id: FlashcardId, rating: Rating):
        pass
