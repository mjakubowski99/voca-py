from src.flashcard.application.exercise.unscramble_word_exercise_factory import (
    UnscrambleWordExerciseFactory,
)
from src.flashcard.application.exercise.word_match_exercise_factory import (
    WordMatchExerciseFactory,
)
from src.flashcard.application.exercise.iflashcard_exercise_factory import IFlashcardExerciseFactory
from src.shared.enum import ExerciseType


class FlashcardSummaryFactory:
    def __init__(
        self,
        unscramble_factory: UnscrambleWordExerciseFactory,
        word_match_factory: WordMatchExerciseFactory,
    ):
        self.unscramble_factory = unscramble_factory
        self.word_match_factory = word_match_factory

    def make(self, exercise_type: ExerciseType) -> IFlashcardExerciseFactory:
        """
        Return the appropriate exercise flashcard factory based on the exercise type.
        """
        if exercise_type == ExerciseType.UNSCRAMBLE_WORDS:
            return self.unscramble_factory
        elif exercise_type == ExerciseType.WORD_MATCH:
            return self.word_match_factory

        raise ValueError(f"Unsupported exercise type: {exercise_type}")
