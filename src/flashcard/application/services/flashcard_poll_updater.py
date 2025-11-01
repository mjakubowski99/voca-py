from src.flashcard.application.contracts import IRepetitionAlgorithmDTO
from src.flashcard.application.repository.contracts import (
    IFlashcardPollRepository,
)
from src.flashcard.domain.models.leitner_level_update import LeitnerLevelUpdate


class FlashcardPollUpdater:
    def __init__(self, poll_repository: IFlashcardPollRepository):
        self.poll_repository = poll_repository

    async def handle(self, dto: IRepetitionAlgorithmDTO) -> None:
        """
        Process all rated flashcards and update their Leitner levels in the poll repository.
        """
        for flashcard_id in dto.get_rated_session_flashcard_ids():
            if not dto.update_poll(flashcard_id):
                continue

            update = LeitnerLevelUpdate(
                user_id=dto.get_user_id_for_flashcard(flashcard_id),
                flashcard_ids=[dto.get_flashcard_id(flashcard_id)],
                leitner_level_increment_step=dto.get_flashcard_rating(flashcard_id).leitner_level(),
            )

            await self.poll_repository.save_leitner_level_update(update)
