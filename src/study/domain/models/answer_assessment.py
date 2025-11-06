from pydantic import BaseModel, Field
from typing import Any
from src.study.domain.value_objects import ExerciseEntryId


class AnswerAssessment(BaseModel):
    exercise_entry_id: ExerciseEntryId = Field(..., alias="exercise_entry_id")
    score: float
    hints_score: float
    correct_answer: str
    user_answer: str

    def is_correct(self) -> bool:
        """Equivalent of PHP's isCorrect()"""
        return self.score >= 100

    def get_real_score(self) -> float:
        """Equivalent of PHP's getRealScore()"""
        return self.score - self.hints_score if self.score > self.hints_score else 0.0

    def get_user_answer(self) -> str:
        return self.user_answer

    def get_correct_answer(self) -> str:
        return self.correct_answer
