from __future__ import annotations
from pydantic import Field
from typing import Type

from src.study.domain.models.answer.answer import Answer
from src.study.domain.value_objects import ExerciseEntryId


class UnscrambleWordAnswer(Answer):
    """Concrete implementation of Answer for unscramble-word exercises."""

    unscrambled_word: str
    hints_count: int = Field(default=0)

    @classmethod
    def from_string(
        cls: Type["UnscrambleWordAnswer"], id: ExerciseEntryId, answer: str
    ) -> "UnscrambleWordAnswer":
        """Equivalent to PHP's fromString() factory."""
        return cls(answer_entry_id=id, unscrambled_word=answer)

    @classmethod
    def from_string_with_hints(
        cls: Type["UnscrambleWordAnswer"], id: ExerciseEntryId, answer: str, hints_count: int
    ) -> "UnscrambleWordAnswer":
        """Equivalent to PHP's fromStringWithHints() factory."""
        return cls(answer_entry_id=id, unscrambled_word=answer, hints_count=hints_count)

    def set_hints_count(self, hints_count: int) -> None:
        """Equivalent to setHintsCount()."""
        self.hints_count = hints_count

    def get_hints_count(self) -> int:
        return self.hints_count

    def to_string(self) -> str:
        return self.unscrambled_word

    def get_compare_score(self, answer: "Answer") -> float:
        """Return 100 if the answers match (case-insensitive), else 0."""
        if not isinstance(answer, UnscrambleWordAnswer):
            raise ValueError("Expected UnscrambleWordAnswer instance for comparison.")

        correct = answer.to_string().strip().lower() == self.to_string().strip().lower()
        return 100.0 if correct else 0.0

    def get_hints_score(self, answer: "Answer") -> float:
        """Calculate the percentage penalty for hints used."""
        if not isinstance(answer, UnscrambleWordAnswer):
            raise ValueError("Expected UnscrambleWordAnswer instance for comparison.")

        word_length = len(answer.to_string())
        if word_length == 0:
            return 0.0
        return round(answer.get_hints_count() / word_length * 100, 2)
