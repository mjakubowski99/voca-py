from abc import ABC, abstractmethod
from src.shared.value_objects.flashcard_id import FlashcardId
from src.shared.value_objects.user_id import UserId
from src.study.domain.enum import Rating


class IRepetitionAlgorithm(ABC):
    @abstractmethod
    async def handle(self, flashcard_id: FlashcardId, user_id: UserId, rating: Rating) -> None:
        """
        Process a repetition algorithm for the given DTO.
        """
        pass
