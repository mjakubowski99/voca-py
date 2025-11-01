from src.flashcard.application.services.irepetition_algorithm import IRepetitionAlgorithm
from src.flashcard.application.repository.contracts import IRateableSessionFlashcardsRepository
from pydantic import BaseModel
from src.flashcard.domain.value_objects import SessionFlashcardId
from src.flashcard.domain.enum import Rating
from typing import List
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import SessionId


class UnauthorizedException(Exception):
    pass


class FlashcardRating(BaseModel):
    session_flashcard_id: SessionFlashcardId
    rating: Rating


class RateFlashcards(BaseModel):
    user_id: UserId
    session_id: SessionId
    ratings: List[FlashcardRating]


class RateFlashcardsHandler:
    def __init__(
        self,
        repository: IRateableSessionFlashcardsRepository,
        repetition_algorithm: IRepetitionAlgorithm,
    ):
        self.repository = repository
        self.repetition_algorithm = repetition_algorithm

    async def handle(self, command: RateFlashcards) -> None:
        session_flashcards = await self.repository.find(command.session_id)

        if session_flashcards.get_session_user_id() != command.user_id:
            raise UnauthorizedException("User is not session owner")

        for rating in command.ratings:
            session_flashcards.rate(rating.session_flashcard_id, rating.rating)

        await self.repository.save(session_flashcards)
        await self.repetition_algorithm.handle(session_flashcards)
