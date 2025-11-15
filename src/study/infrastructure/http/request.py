from typing import List, Optional
from pydantic import BaseModel, Field
from src.study.domain.enum import Rating, SessionType
from src.study.domain.models import answer_assessment


class CreateSessionRequest(BaseModel):
    flashcard_deck_id: Optional[int] = Field(None, description="Flashcard deck ID")
    session_type: SessionType = Field(..., description="Session type")
    cards_per_session: int = Field(..., description="Limit")


class RatingItem(BaseModel):
    id: int = Field(..., description="Learning step ID")
    rating: Rating = Field(..., description="Rating")


class RateFlashcardRequest(BaseModel):
    ratings: List[RatingItem] = Field(..., description="Ratings")


class AnswerItem(BaseModel):
    exercise_entry_id: int = Field(..., description="Exercise entry ID")
    answer: str = Field(..., description="Answer")


class AnswerWordMatchExerciseRequest(BaseModel):
    answers: List[AnswerItem] = Field(..., description="Answers")


class AnswerUnscrambleWordsExerciseRequest(BaseModel):
    answer: str = Field(..., description="Unscrambled word")
    hints_count: int = Field(0, description="Hints count")
