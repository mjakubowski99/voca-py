from src.flashcard.application.contracts import IRepetitionAlgorithmDTO
from src.flashcard.application.repository.contracts import (
    IFlashcardPollRepository,
)
from src.flashcard.domain.enum import Rating
from src.flashcard.domain.models.leitner_level_update import LeitnerLevelUpdate
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.user_id import UserId


class FlashcardPollUpdater:
    def __init__(self, poll_repository: IFlashcardPollRepository):
        self.poll_repository = poll_repository

    async def handle(self, flashcard_id: FlashcardId, user_id: UserId, rating: Rating) -> None:
        update = LeitnerLevelUpdate(
            user_id=user_id,
            flashcard_ids=[flashcard_id],
            leitner_level_increment_step=rating.leitner_level(),
        )

        await self.poll_repository.save_leitner_level_update(update)
