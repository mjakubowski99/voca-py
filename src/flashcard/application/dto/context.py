from pydantic import BaseModel
from src.shared.value_objects.user_id import UserId


class Context(BaseModel):
    user_id: UserId
    max_flashcards_count: int
    current_session_flashcards_count: int
    has_flashcard_poll: bool
    has_deck: bool
