from __future__ import annotations
from typing import List, Optional
from pydantic import Field

# --- Domain imports ---
from src.study.domain.models.exercise.exercise import Exercise
from src.study.domain.models.exercise_entry.word_match_exercise_entry import (
    WordMatchExerciseEntry,
)
from ..answer.answer import Answer
from ..answer_assessment import AnswerAssessment
from src.study.domain.enum import ExerciseStatus
from src.study.domain.enum import ExerciseType
from src.study.domain.value_objects import ExerciseId
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.story_id import StoryId


class WordMatchExercise(Exercise):
    """Concrete exercise for word-match tasks."""

    story_id: Optional[StoryId] = None
    word_match_entries: List[WordMatchExerciseEntry] = Field(default_factory=list)
    options: List[str] = Field(default_factory=list)

    def __init__(
        self,
        story_id: Optional[StoryId],
        exercise_id: ExerciseId,
        user_id: UserId,
        status: ExerciseStatus,
        exercise_entries: List[WordMatchExerciseEntry],
        options: List[str],
    ):
        super().__init__(
            id=exercise_id,
            user_id=user_id,
            exercise_entries=exercise_entries,
            status=status,
            type=ExerciseType.WORD_MATCH,
        )
        object.__setattr__(self, "story_id", story_id)
        object.__setattr__(self, "word_match_entries", exercise_entries)
        object.__setattr__(self, "options", options)

    # --- domain behavior ---
    def assess_answer(self, answer: Answer) -> AnswerAssessment:
        """Assess an answer and filter out correct options."""
        assessment = super().assess_answer(answer)

        if assessment.is_correct():
            lowered = answer.to_string().lower()
            filtered = [opt for opt in self.options if opt.lower() != lowered]
            object.__setattr__(self, "options", filtered)

        return assessment

    # --- getters ---
    def get_story_id(self) -> Optional[StoryId]:
        return self.story_id

    def get_exercise_entries(self) -> List[WordMatchExerciseEntry]:
        return self.word_match_entries

    def get_options(self) -> List[str]:
        return self.options
