from abc import ABC, abstractmethod
from typing import List, Optional

from src.flashcard.domain.enum import FlashcardOwnerType
from src.shared.value_objects.flashcard_id import FlashcardId
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId

from src.shared.models import Emoji
from src.shared.value_objects.language import Language
from src.shared.user.iuser import IUser
from src.study.domain.enum import Rating
from src.shared.value_objects.story_id import StoryId


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
    def get_owner_type(self) -> FlashcardOwnerType:
        pass


class IFlashcardGroupItem(ABC):
    @abstractmethod
    def get_story_id(self) -> Optional[StoryId]:
        pass

    @abstractmethod
    def get_index(self) -> int:
        pass

    @abstractmethod
    def get_flashcard(self) -> IFlashcard:
        pass


class IFlashcardGroup(ABC):
    @abstractmethod
    def get_story_id(self) -> Optional[StoryId]:
        pass

    @abstractmethod
    def get_flashcards(self) -> List[IFlashcardGroupItem]:
        pass


class IFlashcardFacade(ABC):
    """Interfejs fasady do zarządzania fiszkami."""

    @abstractmethod
    async def get_flashcard(self, id: FlashcardId) -> IFlashcard:
        pass

    @abstractmethod
    async def pick_flashcard(self, context: IPickingContext) -> IFlashcard:
        pass

    @abstractmethod
    async def pick_flashcards(self, context: IPickingContext, limit: int) -> List[IFlashcard]:
        pass

    @abstractmethod
    async def pick_group(self, context: IPickingContext) -> IFlashcardGroup:
        pass

    @abstractmethod
    async def new_rating(self, rating_context: IRatingContext):
        pass

    @abstractmethod
    async def delete_user_data(self, user_id):
        """Delete all flashcard-related data for a user."""
        pass

    @abstractmethod
    async def post_language_update(self, user: IUser):
        """Clear flashcard poll after language preferences update."""
        pass
