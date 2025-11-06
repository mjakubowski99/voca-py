from __future__ import annotations
from abc import ABC
from typing import List, Optional
from pydantic import BaseModel, Field

# --- dependencies (from your previous translations) ---
from src.study.domain.models.answer.answer import Answer
from src.study.domain.models.answer_assessment import AnswerAssessment
from src.study.domain.models.exercise_entry.exercise_entry import ExerciseEntry
from src.study.domain.enum import ExerciseStatus
from src.study.domain.enum import ExerciseType
from src.shared.value_objects.user_id import UserId
from src.study.domain.value_objects import ExerciseId


# --- domain exceptions ---
class ExerciseEntryNotFoundException(Exception):
    pass


class ExerciseStatusTransitionException(Exception):
    def __init__(self, current_status: ExerciseStatus, new_status: ExerciseStatus):
        super().__init__(f"Cannot transition from {current_status} to {new_status}")


class ExerciseAssessmentNotAllowedException(Exception):
    pass


class Exercise(BaseModel, ABC):
    """Abstract base class for all exercise types."""

    id: ExerciseId
    user_id: UserId
    exercise_entries: List[ExerciseEntry]
    status: ExerciseStatus
    type: ExerciseType
    updated_entries: List[ExerciseEntry] = Field(default_factory=list, exclude=True)

    # --- domain behavior ---
    def get_id(self) -> ExerciseId:
        return self.id

    def get_user_id(self) -> UserId:
        return self.user_id

    def get_status(self) -> ExerciseStatus:
        return self.status

    def get_exercise_type(self) -> ExerciseType:
        return self.type

    def skip_exercise(self) -> None:
        self.set_status(ExerciseStatus.SKIPPED)

    def mark_as_finished(self) -> None:
        self.set_status(ExerciseStatus.DONE)

    def set_status(self, status: ExerciseStatus) -> None:
        """Allows transitions only from NEW or IN_PROGRESS."""
        if self.status in (ExerciseStatus.NEW, ExerciseStatus.IN_PROGRESS):
            self.status = status
        else:
            raise ExerciseStatusTransitionException(self.status, status)

    def assess_answer(self, answer: Answer) -> AnswerAssessment:
        """Perform answer assessment and update entry & exercise state."""
        if not self._status_allows_for_assessment():
            raise ExerciseAssessmentNotAllowedException(
                f"Exercise status does not allow for assessment. Current status: {self.status.name}"
            )

        entry = self._find_or_fail_exercise_entry(answer)
        assessment = entry.get_correct_answer().compare(answer)

        entry.set_last_user_answer(answer, assessment)

        # handle status transitions
        if self.status == ExerciseStatus.NEW:
            self.set_status(ExerciseStatus.IN_PROGRESS)
        if self.all_answers_correct():
            self.set_status(ExerciseStatus.DONE)

        return assessment

    def get_exercise_entries(self) -> List[ExerciseEntry]:
        return self.exercise_entries

    def get_updated_entries(self) -> List[ExerciseEntry]:
        return [entry for entry in self.exercise_entries if entry.is_updated()]

    def all_answers_correct(self) -> bool:
        """Return True if every exercise entry has a correct answer."""
        return all(entry.is_last_answer_correct() for entry in self.exercise_entries)

    # --- private helpers ---
    def _status_allows_for_assessment(self) -> bool:
        return self.status in (ExerciseStatus.NEW, ExerciseStatus.IN_PROGRESS)

    def _find_or_fail_exercise_entry(self, answer: Answer) -> ExerciseEntry:
        entry = self._find_exercise_entry(answer)
        if entry is None:
            raise ExerciseEntryNotFoundException("Exercise entry with given id not found")
        return entry

    def _find_exercise_entry(self, answer: Answer) -> Optional[ExerciseEntry]:
        for entry in self.exercise_entries:
            if entry.get_id() == answer.get_exercise_entry_id():
                return entry
        return None
