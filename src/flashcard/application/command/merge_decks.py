from typing import Optional
from fastapi import HTTPException
from src.flashcard.application.repository.contracts import (
    IFlashcardDeckRepository,
    IFlashcardRepository,
)
from src.shared.user.iuser import IUser
from src.flashcard.domain.value_objects import FlashcardDeckId


class MergeDecks:
    def __init__(
        self, deck_repository: IFlashcardDeckRepository, flashcard_repository: IFlashcardRepository
    ):
        self.deck_repository = deck_repository
        self.flashcard_repository = flashcard_repository

    async def handle(
        self,
        user: IUser,
        from_deck_id: FlashcardDeckId,
        to_deck_id: FlashcardDeckId,
        new_name: Optional[str] = None,
    ) -> None:
        from_deck = await self.deck_repository.find_by_id(from_deck_id)
        to_deck = await self.deck_repository.find_by_id(to_deck_id)

        if (
            from_deck.owner.is_admin()
            or from_deck.owner.id.get_value() != user.get_id().get_value()
        ):
            raise HTTPException(status_code=403, detail="You are not allowed to merge this deck")

        if to_deck.owner.is_admin() or to_deck.owner.id.get_value() != user.get_id().get_value():
            raise HTTPException(status_code=403, detail="You are not allowed to merge this deck")

        await self.flashcard_repository.replace_deck(from_deck_id, to_deck_id)

        await self.flashcard_repository.replace_in_sessions(from_deck_id, to_deck_id)

        if new_name:
            to_deck.name = new_name
            await self.deck_repository.update(to_deck)

        await self.deck_repository.remove(from_deck)
