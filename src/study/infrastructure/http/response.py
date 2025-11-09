from src.flashcard.domain.enum import FlashcardOwnerType
from src.shared.enum import Language
from typing import List
from typing import Optional

from pydantic import BaseModel, Field


class FlashcardResponse(BaseModel):
    id: int = Field(..., description="Flashcard ID")
    front_word: str = Field(..., description="Front word")
    front_lang: Language = Field(..., description="Front language")
    back_word: str = Field(..., description="Back word")
    back_lang: Language = Field(..., description="Back language")
    front_context: str = Field(..., description="Front context")
    back_context: str = Field(..., description="Back context")
    emoji: Optional[str] = Field(..., description="Emoji")
    owner_type: FlashcardOwnerType = Field(..., description="Owner type")


class IndexedKeyboardResponse(BaseModel):
    c: str = Field(..., description="Character")
    i: int = Field(..., description="Index")


class UnscrambleWordExerciseResponse(BaseModel):
    id: int = Field(..., description="Exercise ID")
    exercise_entry_id: int = Field(..., description="Exercise entry ID")
    front_word: str = Field(..., description="Front word")
    context_sentence: str = Field(..., description="Context sentence")
    context_sentence_translation: str = Field(..., description="Context sentence translation")
    back_word: str = Field(..., description="Back word")
    emoji: Optional[str] = Field(..., description="Emoji")
    keyboard: List[str] = Field(..., description="Keyboard")
    indexed_keyboard: List[IndexedKeyboardResponse] = Field(..., description="Indexed keyboard")


class WordMatchExerciseResponse(BaseModel):
    id: int = Field(..., description="Exercise ID")
    exercise_entry_id: int = Field(..., description="Exercise entry ID")
    front_word: str = Field(..., description="Front word")
    context_sentence: str = Field(..., description="Context sentence")
    context_sentence_translation: str = Field(..., description="Context sentence translation")
    back_word: str = Field(..., description="Back word")
    emoji: Optional[str] = Field(..., description="Emoji")


class LearningSessionResponse(BaseModel):
    id: int = Field(..., description="Learning session ID")
    cards_per_session: int = Field(..., description="Cards per session")
    is_finished: bool = Field(..., description="Whether the session is finished")
    progress: int = Field(..., description="Progress")
    is_exercise_mode: bool = Field(..., description="Whether the session is in exercise mode")
    score: bool = Field(..., description="Whether the session is scored")
    next_flashcards: List[FlashcardResponse] = Field(..., description="Next flashcards")
    next_exercises: List[UnscrambleWordExerciseResponse | WordMatchExerciseResponse] = Field(
        ..., description="Next exercises"
    )
