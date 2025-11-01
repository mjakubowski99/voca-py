from abc import ABC, abstractmethod
from typing import List
from src.shared.enum import Language
from src.shared.value_objects.user_id import UserId
from flashcard.domain.models.flashcard import Flashcard
from flashcard.domain.models.next_session_flashcards import NextSessionFlashcards


class IFlashcardSelector(ABC):
    @abstractmethod
    async def reset_repetitions_in_session(self, user_id: UserId) -> None:
        """Reset repetitions for all flashcards in the session for the given user."""
        pass

    @abstractmethod
    async def select_to_poll(
        self,
        user_id: UserId,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        """Select flashcards to include in a poll."""
        pass

    @abstractmethod
    async def select(
        self,
        next_session_flashcards: NextSessionFlashcards,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        """Select flashcards for the next session."""
        pass

    @abstractmethod
    async def select_from_poll(
        self,
        next_session_flashcards: NextSessionFlashcards,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        """Select flashcards from the poll for the next session."""
        pass
