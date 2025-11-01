from abc import ABC, abstractmethod
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.next_session_flashcards import NextSessionFlashcards
from src.flashcard.domain.models.session_flashcard_summaries import SessionFlashcardSummaries


class IFlashcardExerciseFactory(ABC):
    @abstractmethod
    async def make(
        self,
        next_session_flashcards: NextSessionFlashcards,
        base_flashcard: Flashcard,
    ) -> SessionFlashcardSummaries:
        """
        Generate session flashcard summaries based on a base flashcard and the next session flashcards.
        """
        pass
