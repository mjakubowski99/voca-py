from typing import List
from src.flashcard.domain.models.next_session_flashcards import NextSessionFlashcards
from src.flashcard.domain.models.flashcard import Flashcard


class SessionFlashcardsService:
    async def add(
        self, session_flashcards: NextSessionFlashcards, flashcards: List[Flashcard]
    ) -> NextSessionFlashcards:
        for flashcard in flashcards:
            if not session_flashcards.can_add_next():
                break
            session_flashcards.add_next(flashcard)

        return session_flashcards
