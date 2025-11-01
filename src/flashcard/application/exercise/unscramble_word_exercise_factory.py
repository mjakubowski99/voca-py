from src.flashcard.application.exercise.iflashcard_exercise_factory import IFlashcardExerciseFactory
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.next_session_flashcards import NextSessionFlashcards
from src.flashcard.domain.models.session_flashcard_summaries import SessionFlashcardSummaries


class UnscrambleWordExerciseFactory(IFlashcardExerciseFactory):
    async def make(
        self,
        next_session_flashcards: NextSessionFlashcards,
        base_flashcard: Flashcard,
    ) -> SessionFlashcardSummaries:
        """
        Generate a session summary for the Unscramble Word exercise.
        Returns only the base flashcard wrapped in a SessionFlashcardSummaries object.
        """
        return SessionFlashcardSummaries.from_flashcards([base_flashcard], base_flashcard)
