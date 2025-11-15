from src.flashcard.application.repository.contracts import IFlashcardReadRepository
from src.flashcard.domain.enum import FlashcardOwnerType
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.application.dto.rating_stats import RatingStats
from src.shared.user.iuser import IUser


class GetRatingStats:
    def __init__(self, repository: IFlashcardReadRepository):
        self.repository = repository

    async def get_for_deck(self, user: IUser, deck_id: FlashcardDeckId) -> RatingStats:
        return await self.repository.find_flashcard_stats(
            user.get_user_language().get_enum(),
            user.get_learning_language().get_enum(),
            deck_id,
            user.get_id(),
        )

    async def get_for_user(self, user: IUser) -> RatingStats:
        return await self.repository.find_flashcard_stats(
            user.get_user_language().get_enum(),
            user.get_learning_language().get_enum(),
            None,
            user.get_id(),
            FlashcardOwnerType.USER,
        )

    async def get_for_admin(self, user: IUser) -> RatingStats:
        return await self.repository.find_flashcard_stats(
            user.get_user_language().get_enum(),
            user.get_learning_language().get_enum(),
            None,
            user.get_id(),
            FlashcardOwnerType.ADMIN,
        )
