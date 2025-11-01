from typing import List
from src.shared.enum import Language
from src.shared.value_objects.user_id import UserId
from flashcard.domain.models.flashcard import Flashcard
from flashcard.domain.models.next_session_flashcards import NextSessionFlashcards
from src.flashcard.application.repository.contracts import ISmTwoFlashcardRepository
from src.flashcard.application.repository.contracts import IFlashcardRepository
from src.flashcard.application.repository.contracts import IFlashcardPollRepository
from src.flashcard.application.repository.contracts import FlashcardSortCriteria
from src.flashcard.application.services.iflashcard_selector import IFlashcardSelector


class SmTwoFlashcardSelector(IFlashcardSelector):
    def __init__(
        self,
        repository: ISmTwoFlashcardRepository,
        flashcard_repository: IFlashcardRepository,
        pool_repository: IFlashcardPollRepository,
    ):
        self.repository = repository
        self.flashcard_repository = flashcard_repository
        self.pool_repository = pool_repository

    async def reset_repetitions_in_session(self, user_id: UserId) -> None:
        await self.repository.reset_repetitions_in_session(user_id)

    async def select_to_poll(
        self,
        user_id: UserId,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        criteria = [
            FlashcardSortCriteria.PLANNED_FLASHCARDS_FOR_CURRENT_DATE_FIRST,
            FlashcardSortCriteria.OLDER_THAN_FIFTEEN_SECONDS_AGO,
            FlashcardSortCriteria.HARD_FLASHCARDS_FIRST,
            FlashcardSortCriteria.OLDEST_UPDATE_FLASHCARDS_FIRST,
            FlashcardSortCriteria.HARD_FLASHCARDS_FIRST,
            FlashcardSortCriteria.RANDOMIZE_LATEST_FLASHCARDS_ORDER,
            FlashcardSortCriteria.OLDEST_UPDATE_FLASHCARDS_FIRST,
        ]

        return await self.repository.get_next_flashcards_by_user(
            user_id,
            limit,
            exclude_flashcard_ids,
            criteria,
            limit,
            from_poll=False,
            exclude_from_poll=True,
            front=front,
            back=back,
        )

    async def select(
        self,
        next_session_flashcards: NextSessionFlashcards,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        flashcards: List[Flashcard] = []

        if next_session_flashcards.has_flashcard_poll():
            flashcards = await self.select_from_poll(
                next_session_flashcards, limit, front, back, exclude_flashcard_ids
            )
        elif next_session_flashcards.has_deck():
            return await self._select_from_deck(
                next_session_flashcards, limit, front, back, exclude_flashcard_ids
            )

        if not flashcards:
            return await self._select_from_all(
                next_session_flashcards, limit, front, back, exclude_flashcard_ids
            )

        return flashcards

    async def select_from_poll(
        self,
        next_session_flashcards: NextSessionFlashcards,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        flashcard_ids = await self.pool_repository.select_next_leitner_flashcard(
            next_session_flashcards.get_user_id(),
            exclude_flashcard_ids,
            limit,
        )
        return await self.flashcard_repository.find_many(flashcard_ids)

    async def _select_from_all(
        self,
        next_session_flashcards: NextSessionFlashcards,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        latest_limit = max(3, int(next_session_flashcards.get_max_flashcards_count() * 0.2))
        latest_limit = min(5, latest_limit)
        prioritize_not_hard = (
            next_session_flashcards.get_current_session_flashcards_count() % 5 == 0
        )

        latest_ids = await self.flashcard_repository.get_latest_session_flashcard_ids(
            next_session_flashcards.get_session_id(),
            latest_limit,
        )
        exclude_flashcard_ids = list(set(exclude_flashcard_ids + latest_ids))

        criteria = FlashcardSortCriteria.default_criteria(prioritize_not_hard)

        results = await self.repository.get_next_flashcards_by_user(
            next_session_flashcards.get_user_id(),
            limit,
            exclude_flashcard_ids,
            criteria,
            next_session_flashcards.get_max_flashcards_count(),
            from_poll=False,
            exclude_from_poll=False,
            front=front,
            back=back,
        )

        if len(results) < limit:
            return await self.repository.get_next_flashcards_by_user(
                next_session_flashcards.get_user_id(),
                limit,
                [],
                criteria,
                next_session_flashcards.get_max_flashcards_count(),
                from_poll=False,
                exclude_from_poll=False,
                front=front,
                back=back,
            )

        return results

    async def _select_from_deck(
        self,
        next_session_flashcards: NextSessionFlashcards,
        limit: int,
        front: Language,
        back: Language,
        exclude_flashcard_ids: List[int] = [],
    ) -> List[Flashcard]:
        latest_limit = max(3, int(next_session_flashcards.get_max_flashcards_count() * 0.2))
        latest_limit = min(5, latest_limit)
        prioritize_not_hard = (
            next_session_flashcards.get_current_session_flashcards_count() % 5 == 0
        )

        latest_ids = await self.flashcard_repository.get_latest_session_flashcard_ids(
            next_session_flashcards.get_session_id(),
            latest_limit,
        )
        exclude_flashcard_ids = list(set(exclude_flashcard_ids + latest_ids))

        deck = next_session_flashcards.get_deck()
        criteria = FlashcardSortCriteria.deck_criteria(prioritize_not_hard)

        results = await self.repository.get_next_flashcards_by_deck(
            next_session_flashcards.get_user_id(),
            deck.get_id(),
            limit,
            exclude_flashcard_ids,
            criteria,
            next_session_flashcards.get_max_flashcards_count(),
            from_poll=False,
            front=front,
            back=back,
        )

        if len(results) < limit:
            return await self.repository.get_next_flashcards_by_deck(
                next_session_flashcards.get_user_id(),
                deck.get_id(),
                limit,
                [],
                criteria,
                next_session_flashcards.get_max_flashcards_count(),
                from_poll=False,
                front=front,
                back=back,
            )

        return results
