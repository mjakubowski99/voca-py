from dataclasses import dataclass
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.models.flashcard_poll import FlashcardPoll
from src.flashcard.application.repository.contracts import IFlashcardPollRepository


@dataclass
class FlashcardPollResolver:
    repository: IFlashcardPollRepository
    LEARNT_CARDS_PURGE_LIMIT: int = 10

    async def resolve(self, user_id: UserId) -> FlashcardPoll:
        try:
            return await self.repository.find_by_user(user_id, self.LEARNT_CARDS_PURGE_LIMIT)
        except Exception as exc:
            count_to_purge = exc.current_size - exc.expected_max_size

            await self.repository.purge_latest_flashcards(user_id, count_to_purge)

            return await self.repository.find_by_user(user_id, self.LEARNT_CARDS_PURGE_LIMIT)
