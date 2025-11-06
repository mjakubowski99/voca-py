from typing import Optional
from pydantic import BaseModel
from src.flashcard.application.dto.general_rating import GeneralRating
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.language import Language
from src.shared.enum import LanguageLevel
from src.flashcard.domain.enum import FlashcardOwnerType
from src.shared.models import Emoji


# Flashcard DTO
class FlashcardRead(BaseModel):
    id: FlashcardId
    front_word: str
    front_lang: Language
    back_word: str
    back_lang: Language
    front_context: str
    back_context: str
    general_rating: GeneralRating
    language_level: LanguageLevel
    rating_percentage: float
    emoji: Optional[Emoji]
    owner_type: FlashcardOwnerType

    model_config = {"arbitrary_types_allowed": True}
