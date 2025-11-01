from src.flashcard.application.dto.deck_details_read import DeckDetailsRead
from src.flashcard.application.repository.contracts import IFlashcardDeckReadRepository
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.value_objects.user_id import UserId


class GetDeckDetails:
    def __init__(self, repository: IFlashcardDeckReadRepository):
        self.repository = repository

    async def get(
        self, user_id: UserId, deck_id: FlashcardDeckId, page: int, per_page: int
    ) -> DeckDetailsRead:
        return await self.repository.find_details(user_id, deck_id, None, page, per_page)
