from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

# Zakładamy, że te klasy są już zdefiniowane:
from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.domain.models.answer.answer import Answer
from src.study.domain.models.answer_assessment import AnswerAssessment
from src.study.domain.value_objects import ExerciseEntryId
from src.study.domain.value_objects import ExerciseId


class ExerciseEntry(BaseModel):
    """Reprezentuje pojedynczy wpis ćwiczenia (ExerciseEntry)"""

    id: ExerciseEntryId
    exercise_id: ExerciseId
    flashcard_id: FlashcardId
    correct_answer: Answer
    last_user_answer: Optional[Answer] = None
    last_answer_correct: Optional[bool] = None
    order: int
    score: float = 0.0
    answers_count: int = 0
    updated: bool = Field(default=False, exclude=True)

    # --- Domain methods (PHP equivalents) ---
    def get_id(self) -> ExerciseEntryId:
        return self.id

    def get_score(self) -> float:
        return self.score

    def get_answers_count(self) -> int:
        return self.answers_count

    def get_exercise_id(self) -> ExerciseId:
        return self.exercise_id

    def get_correct_answer(self) -> Answer:
        return self.correct_answer

    def get_last_user_answer(self) -> Optional[Answer]:
        return self.last_user_answer

    def is_last_answer_correct(self) -> bool:
        return bool(self.last_answer_correct)

    def is_updated(self) -> bool:
        return self.updated

    def get_order(self) -> int:
        return self.order

    def set_last_user_answer(self, answer: Answer, assessment: AnswerAssessment) -> None:
        """Ustawia ostatnią odpowiedź użytkownika i aktualizuje wynik"""
        self.last_user_answer = answer
        self.answers_count += 1
        self._recalculate_score_based_on_assessment(assessment)
        self._set_last_user_answer_correct(assessment.is_correct())
        self.updated = True

    # --- private helpers ---
    def _set_last_user_answer_correct(self, is_correct: bool) -> None:
        self.last_answer_correct = is_correct
        self.updated = True

    def _recalculate_score_based_on_assessment(self, assessment: AnswerAssessment) -> None:
        """Przelicza średni wynik bazując na ocenie odpowiedzi"""
        total_score = self.score + assessment.get_real_score()
        self.score = total_score / self.answers_count if self.answers_count > 0 else 0.0
