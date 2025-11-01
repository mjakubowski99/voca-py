from typing import List, Optional
from src.flashcard.application.repository.contracts import IFlashcardDeckReadRepository
from src.flashcard.application.dto.owner_deck_read import OwnerDeckRead
from src.shared.enum import LanguageLevel
from src.shared.user.iuser import IUser


class GetUserDecks:
    def __init__(self, repository: IFlashcardDeckReadRepository):
        self.repository = repository

    async def get(
        self, user: IUser, search: Optional[str], page: int, per_page: int
    ) -> List[OwnerDeckRead]:
        return await self.repository.get_by_user(
            user.get_id(),
            user.get_user_language().get_enum(),
            user.get_learning_language().get_enum(),
            search,
            page,
            per_page,
        )


class GetAdminDecks:
    def __init__(self, repository: IFlashcardDeckReadRepository):
        self.repository = repository

    async def get(
        self,
        user: IUser,
        level: Optional[LanguageLevel],
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> List[OwnerDeckRead]:
        return await self.repository.get_admin_decks(
            user.get_id(),
            user.get_user_language().get_enum(),
            user.get_learning_language().get_enum(),
            level,
            search,
            page,
            per_page,
        )
