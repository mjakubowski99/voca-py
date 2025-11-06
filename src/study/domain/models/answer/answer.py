from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type, TypeVar
from src.study.domain.value_objects import ExerciseEntryId
from src.study.domain.models.answer_assessment import AnswerAssessment


class ExerciseAnswerCompareFailureException(Exception):
    """Raised when comparing answers with mismatched exercise entry IDs."""

    pass


T = TypeVar("T", bound="Answer")


class Answer(BaseModel, ABC):
    """Abstract base class for an Answer value object."""

    answer_entry_id: ExerciseEntryId

    @classmethod
    @abstractmethod
    def from_string(cls: Type[T], id: ExerciseEntryId, answer: str) -> T:
        """Construct an Answer subclass instance from a string."""
        raise NotImplementedError

    def get_exercise_entry_id(self) -> ExerciseEntryId:
        return self.answer_entry_id

    def compare(self, answer: Answer) -> AnswerAssessment:
        """Compare this answer against another one and produce an assessment."""
        if self.get_exercise_entry_id() != answer.get_exercise_entry_id():
            raise ExerciseAnswerCompareFailureException(
                "Trying to compare answers for invalid exercise entry id"
            )

        return AnswerAssessment(
            exercise_entry_id=self.get_exercise_entry_id(),
            score=self.get_compare_score(answer),
            hints_score=self.get_hints_score(answer),
            correct_answer=self.to_string(),
            user_answer=answer.to_string(),
        )

    @abstractmethod
    def to_string(self) -> str:
        """Return the string representation of this answer."""
        raise NotImplementedError

    @abstractmethod
    def get_compare_score(self, answer: Answer) -> float:
        """Return a numeric score for how correct the answer is."""
        raise NotImplementedError

    @abstractmethod
    def get_hints_score(self, answer: Answer) -> float:
        """Return any score penalty due to hints used."""
        raise NotImplementedError
