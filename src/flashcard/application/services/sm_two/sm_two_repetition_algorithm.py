from collections import defaultdict
from src.flashcard.application.contracts import IRepetitionAlgorithmDTO
from src.flashcard.application.services.flashcard_poll_updater import FlashcardPollUpdater
from src.flashcard.application.services.irepetition_algorithm import IRepetitionAlgorithm
from src.flashcard.application.repository.contracts import (
    ISmTwoFlashcardRepository,
)
from src.shared.value_objects.user_id import UserId


class SmTwoRepetitionAlgorithm(IRepetitionAlgorithm):
    def __init__(
        self,
        repository: ISmTwoFlashcardRepository,
        poll_updater: FlashcardPollUpdater,
    ):
        self.repository = repository
        self.poll_updater = poll_updater

    async def handle(self, dto: IRepetitionAlgorithmDTO) -> None:
        rated_flashcard_ids = dto.get_rated_session_flashcard_ids()
        if not rated_flashcard_ids:
            return

        user_flashcard_map: dict[str, list] = defaultdict(list)
        for session_flashcard_id in rated_flashcard_ids:
            user_id = dto.get_user_id_for_flashcard(session_flashcard_id)
            flashcard_id = dto.get_flashcard_id(session_flashcard_id)
            user_flashcard_map[user_id.value].append(flashcard_id)

        for user_id_str, flashcard_ids in user_flashcard_map.items():
            user_id = UserId(user_id_str)

            sm_two_flashcards = await self.repository.find_many(user_id, flashcard_ids)

            for session_flashcard_id in rated_flashcard_ids:
                flashcard_id = dto.get_flashcard_id(session_flashcard_id)
                sm_two_flashcards.fill_if_missing(user_id, flashcard_id)
                sm_two_flashcards.update_by_rating(
                    flashcard_id, dto.get_flashcard_rating(session_flashcard_id)
                )

            await self.repository.save_many(sm_two_flashcards)

            await self.poll_updater.handle(dto)
