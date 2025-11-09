# src/study/domain/models/answer/word_match_answer.py
from __future__ import annotations
from typing import Type
from pydantic import ConfigDict
from src.study.domain.models.answer.answer import Answer
from src.study.domain.value_objects import ExerciseEntryId


class WordMatchAnswer(Answer):
    """Concrete implementation of an Answer for 'word matching' exercises."""

    word: str

    @classmethod
    def from_string(
        cls: Type[WordMatchAnswer], id: ExerciseEntryId, answer: str
    ) -> WordMatchAnswer:
        # przekazujemy poprawnie answer_entry_id z klasy bazowej
        return cls(answer_entry_id=id, word=answer)

    def to_string(self) -> str:
        return self.word

    def get_compare_score(self, answer: Answer) -> float:
        if not isinstance(answer, WordMatchAnswer):
            raise ValueError("Expected WordMatchAnswer instance for comparison.")

        return 100.0 if answer.word.strip().lower() == self.word.strip().lower() else 0.0

    def get_hints_score(self, answer: Answer) -> float:
        return 0.0
