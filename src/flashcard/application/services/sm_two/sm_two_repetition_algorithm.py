from src.flashcard.application.services.flashcard_poll_updater import FlashcardPollUpdater
from src.flashcard.application.services.irepetition_algorithm import IRepetitionAlgorithm
from src.flashcard.application.repository.contracts import (
    ISmTwoFlashcardRepository,
)
from src.flashcard.domain.enum import Rating
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.user_id import UserId


class SmTwoRepetitionAlgorithm(IRepetitionAlgorithm):
    def __init__(
        self,
        repository: ISmTwoFlashcardRepository,
        poll_updater: FlashcardPollUpdater,
    ):
        self.repository = repository
        self.poll_updater = poll_updater

    async def handle(self, flashcard_id: FlashcardId, user_id: UserId, rating: Rating) -> None:
        sm_two_flashcards = await self.repository.find_many(user_id, [flashcard_id])

        sm_two_flashcards.fill_if_missing(user_id, flashcard_id)
        sm_two_flashcards.update_by_rating(flashcard_id, rating)

        await self.repository.save_many(sm_two_flashcards)

        await self.poll_updater.handle(flashcard_id, user_id, rating)
