from typing import Optional
from pydantic import BaseModel, model_validator

from src.flashcard.domain.value_objects import FlashcardId
from src.shared.flashcard.contracts import IFlashcard
from src.study.domain.enum import Rating
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.value_objects import LearningSessionStepId


class LearningSessionStep(BaseModel):
    id: LearningSessionStepId
    rating: Optional[Rating]
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
                "Musi być ustawione jedno z pól: flashcard, unscramble_word_exercise lub word_match."
            )
        if set_count > 1:
            raise ValueError(
                "Tylko jedno z pól flashcard, unscramble_word_exercise, word_match może być ustawione."
            )
        return self

    def get_flashcard_id(self) -> FlashcardId:
        if self.flashcard_exercise:
            return self.flashcard_exercise.get_flashcard_id()
        if self.unscramble_word_exercise:
            return self.unscramble_word_exercise.exercise_entries[0].flashcard_id
        raise Exception("Unknown flashcard type")
