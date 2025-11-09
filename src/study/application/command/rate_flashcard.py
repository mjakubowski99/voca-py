from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.user.iuser import IUser
from src.study.application.dto.rating_context import RatingContext
from src.study.application.repository.contracts import ISessionRepository
from src.study.domain.enum import Rating
from src.study.domain.value_objects import LearningSessionStepId


class RateFlashcard:
    def __init__(self, repository: ISessionRepository, flashcard_facade: IFlashcardFacade):
        self.repository = repository
        self.flashcard_facade = flashcard_facade

    async def handle(self, user: IUser, step_id: LearningSessionStepId, rating: Rating):
        updated_flashcard_id = await self.repository.update_flashcard_rating(step_id, rating)

        rating_context = RatingContext(
            user=user,
            flashcard_id=updated_flashcard_id,
            rating=rating,
        )

        await self.flashcard_facade.new_rating(rating_context)
