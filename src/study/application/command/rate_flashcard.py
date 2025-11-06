from src.shared.flashcard.contracts import IFlashcardFacade
from src.study.domain.enum import Rating
from src.study.domain.value_objects import LearningSessionStepId


class RateFlashcard:
    def __init__(self, repository, flashcard_facade: IFlashcardFacade):
        self.repository = repository
        self.flashcard_facade = flashcard_facade

    async def handle(self, step_id: LearningSessionStepId, rating: Rating):
        updated_flashcard_id = self.repository.update_flashcard_rating(step_id, rating)
        await self.flashcard_facade.new_rating(updated_flashcard_id, rating)
