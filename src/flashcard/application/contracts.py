from abc import ABC, abstractmethod
from typing import List
from src.flashcard.domain.value_objects import SessionFlashcardId, FlashcardId
from src.flashcard.domain.enum import Rating
from src.shared.value_objects.user_id import UserId


class IRepetitionAlgorithmDTO(ABC):
    @abstractmethod
    def get_user_id_for_flashcard(self, flashcard_id: SessionFlashcardId) -> UserId:
        """
        Returns the user ID associated with a specific session flashcard.
        """
        pass

    @abstractmethod
    def get_rated_session_flashcard_ids(self) -> List[SessionFlashcardId]:
        """
        Returns a list of session flashcard IDs that have already been rated.
        """
        pass

    @abstractmethod
    def get_flashcard_id(self, flashcard_id: SessionFlashcardId) -> FlashcardId:
        """
        Returns the FlashcardId associated with a session flashcard ID.
        """
        pass

    @abstractmethod
    def get_flashcard_rating(self, flashcard_id: SessionFlashcardId) -> Rating:
        """
        Returns the Rating for a given session flashcard.
        """
        pass

    @abstractmethod
    def update_poll(self, flashcard_id: SessionFlashcardId) -> bool:
        """
        Updates the flashcard poll if necessary and returns whether it was updated.
        """
        pass
