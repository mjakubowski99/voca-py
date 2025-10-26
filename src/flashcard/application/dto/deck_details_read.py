from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from src.flashcard.application.dto.flashcard_read import FlashcardRead
from src.flashcard.domain.enum import FlashcardOwnerType
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.enum import LanguageLevel


# DeckDetailsRead Pydantic model
class DeckDetailsRead(BaseModel):
    id: FlashcardDeckId
    name: str
    flashcards: List[FlashcardRead]
    page: int
    per_page: int
    count: int
    owner_type: FlashcardOwnerType
    language_level: LanguageLevel
    last_learnt_at: Optional[datetime]
    rating_percentage: float
