from dataclasses import dataclass
from fastapi import HTTPException
from src.flashcard.application.repository.contracts import IFlashcardRepository
from src.flashcard.domain.value_objects import FlashcardId
from src.shared.value_objects.user_id import UserId


@dataclass(frozen=True)
class BulkDeleteFlashcards:
    user_id: UserId
    flashcard_ids: list[FlashcardId]


@dataclass(frozen=True)
class BulkDeleteFlashcardsResult:
    deleted_count: int


class BulkDeleteFlashcardsHandler:
    def __init__(self, flashcard_repository: IFlashcardRepository):
        self.flashcard_repository = flashcard_repository

    async def handle(self, command: BulkDeleteFlashcards) -> BulkDeleteFlashcardsResult:
        if not command.flashcard_ids:
            return BulkDeleteFlashcardsResult(deleted_count=0)

        # Fetch all flashcards to verify ownership
        flashcards = await self.flashcard_repository.find_many(command.flashcard_ids)

        # Check if all requested flashcards were found
        found_ids = {f.id.value for f in flashcards}
        requested_ids = {f.value for f in command.flashcard_ids}
        missing_ids = requested_ids - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Flashcards not found: {sorted(missing_ids)}",
            )

        # Verify that the user owns all flashcards
        unauthorized_flashcards = []
        for flashcard in flashcards:
            # Check if flashcard is user-owned and belongs to the requesting user
            if flashcard.owner.is_user():
                if flashcard.owner.id.value != command.user_id.value:
                    unauthorized_flashcards.append(flashcard.id.value)
            # Admin-owned flashcards cannot be deleted by regular users
            elif flashcard.owner.is_admin():
                unauthorized_flashcards.append(flashcard.id.value)

        if unauthorized_flashcards:
            raise HTTPException(
                status_code=403,
                detail=f"You are not allowed to delete these flashcards: {sorted(unauthorized_flashcards)}",
            )

        # Delete the flashcards
        await self.flashcard_repository.bulk_delete(command.user_id, command.flashcard_ids)

        return BulkDeleteFlashcardsResult(deleted_count=len(command.flashcard_ids))
