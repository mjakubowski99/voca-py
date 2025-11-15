from typing import Optional
from pydantic import BaseModel, model_validator

from src.shared.value_objects.flashcard_id import FlashcardId
from src.shared.flashcard.contracts import IFlashcard
from src.study.domain.enum import ExerciseType, Rating
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.value_objects import ExerciseEntryId, LearningSessionStepId


class LearningSessionStep(BaseModel):
    id: LearningSessionStepId
    rating: Optional[Rating]
    exercise_entry_id: Optional[ExerciseEntryId] = None
    flashcard_exercise: Optional[IFlashcard] = None
    unscramble_word_exercise: Optional[UnscrambleWordExercise] = None
    word_match_exercise: Optional[WordMatchExercise] = None

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def validate_exercise_choice(self):
        exercises = [
            self.flashcard_exercise,
            self.unscramble_word_exercise,
            self.word_match_exercise,
        ]

        set_count = sum(ex is not None for ex in exercises)

        if set_count == 0:
            raise ValueError(
                "Must be set one of the fields: flashcard, unscramble_word_exercise or word_match."
            )
        if set_count > 1:
            raise ValueError(
                "Only one of the fields: flashcard, unscramble_word_exercise, word_match can be set."
            )
        return self

    def get_flashcard_id(self) -> FlashcardId:
        if self.flashcard_exercise:
            return self.flashcard_exercise.get_flashcard_id()
        if self.unscramble_word_exercise:
            return self.unscramble_word_exercise.exercise_entries[0].flashcard_id
        if self.word_match_exercise:
            return self.word_match_exercise.get_current_entry().flashcard_id
        raise Exception("Unknown flashcard type")

    def get_exercise_type(self) -> Optional[ExerciseType]:
        if self.flashcard_exercise:
            return None
        if self.unscramble_word_exercise:
            return ExerciseType.UNSCRAMBLE_WORDS
        if self.word_match_exercise:
            return ExerciseType.WORD_MATCH
        raise Exception("Unknown exercise type")

    def get_exercise_entry_id(self) -> Optional[ExerciseEntryId]:
        return self.exercise_entry_id
