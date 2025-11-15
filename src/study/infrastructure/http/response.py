from src.flashcard.domain.enum import FlashcardOwnerType
from src.shared.enum import Language
from typing import List, Union
from typing import Optional

from pydantic import BaseModel, Field
from src.study.domain.enum import ExerciseType


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
    id: int = Field(..., description="Exercise entry ID")
    is_finished: bool = Field(..., description="Whether the exercise is finished")
    exercise_id: int = Field(..., description="Exercise entry ID")
    is_story: bool = Field(..., description="Whether the exercise is a story")
    word: str = Field(..., description="Word")
    word_translation: str = Field(..., description="Word translation")
    sentence_part_before_word: str = Field(..., description="Sentence part before word")
    sentence_part_after_word: str = Field(..., description="Sentence part after word")
    options: List[str] = Field(..., description="Options")
    previous_entries: List["WordMatchExerciseResponse"] = Field([], description="Previous entries")


class ExerciseWrapperResponse(BaseModel):
    exercise_type: ExerciseType = Field(..., description="Type of exercise")
    links: List[str] = Field(..., description="List of links")
    data: Union[UnscrambleWordExerciseResponse, WordMatchExerciseResponse] = Field(
        ..., description="Exercise data"
    )


class SessionDetailsResponse(BaseModel):
    id: int = Field(..., description="Learning session ID")
    cards_per_session: int = Field(..., description="Cards per session")
    is_finished: bool = Field(..., description="Whether the session is finished")
    progress: int = Field(..., description="Progress")
    is_exercise_mode: bool = Field(..., description="Whether the session is in exercise mode")
    score: int = Field(..., description="Score after session finished")
    next_flashcards: List[FlashcardResponse] = Field(..., description="Next flashcards")
    next_exercises: List[ExerciseWrapperResponse] = Field(..., description="Next exercises")


class LearningSessionResponse(BaseModel):
    session: SessionDetailsResponse = Field(..., description="Session details")
