from typing import List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import FlashcardId
from src.flashcard.domain.models.flashcard_poll import FlashcardPoll
from src.flashcard.domain.models.leitner_level_update import LeitnerLevelUpdate
from src.flashcard.application.repository.contracts import IFlashcardPollRepository
from core.models import FlashcardPollItem


class FlashcardPollRepository(IFlashcardPollRepository):
    async def find_by_user(self, user_id: UserId, learnt_cards_purge_limit: int) -> FlashcardPoll:
        session: AsyncSession = get_session()

        # Fetch flashcards exceeding easy_ratings_count threshold
        stmt = (
            select(FlashcardPollItem)
            .where(FlashcardPollItem.user_id == user_id.value)
            .where(
                FlashcardPollItem.easy_ratings_count
                >= FlashcardPollItem.easy_ratings_count_to_purge
            )
            .limit(learnt_cards_purge_limit)
        )
        result = await session.execute(stmt)
        flashcards_to_reject = [FlashcardId(item.flashcard_id) for item in result.scalars().all()]

        # Count total flashcards
        count_stmt = select(func.count()).where(FlashcardPollItem.user_id == user_id.value)
        count_result = await session.execute(count_stmt)
        total_count = count_result.scalar() or 0

        return FlashcardPoll(
            user_id=user_id,
            poll_size=total_count,
            purge_candidates=flashcards_to_reject,
        )

    async def purge_latest_flashcards(self, user_id: UserId, limit: int) -> None:
        session: AsyncSession = get_session()
        stmt = (
            select(FlashcardPollItem.id)
            .where(FlashcardPollItem.user_id == user_id.value)
            .order_by(FlashcardPollItem.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        ids_to_delete = [row[0] for row in result.all()]
        if ids_to_delete:
            await session.execute(
                delete(FlashcardPollItem).where(FlashcardPollItem.id.in_(ids_to_delete))
            )
            await session.commit()

    async def save_leitner_level_update(self, update_obj: LeitnerLevelUpdate) -> bool:
        session: AsyncSession = get_session()
        stmt = (
            update(FlashcardPollItem)
            .where(FlashcardPollItem.user_id == update_obj.user_id.value)
            .where(FlashcardPollItem.flashcard_id.in_([f.value for f in update_obj.ids]))
            .values(
                leitner_level=FlashcardPollItem.leitner_level
                + update_obj.leitner_level_increment_step
                + 1,
                easy_ratings_count=FlashcardPollItem.easy_ratings_count + 1
                if update_obj.increment_easy_ratings_count()
                else FlashcardPollItem.easy_ratings_count,
            )
        )
        await session.execute(stmt)
        await session.commit()
        return True

    async def save(self, poll: FlashcardPoll) -> None:
        session: AsyncSession = get_session()

        # Delete flashcards to purge
        purge_ids = [f.value for f in poll.flashcard_ids_to_purge]
        if purge_ids:
            await session.execute(
                delete(FlashcardPollItem).where(
                    FlashcardPollItem.user_id == poll.user_id.value,
                    FlashcardPollItem.flashcard_id.in_(purge_ids),
                )
            )

        # Insert new flashcards
        insert_data = []
        if poll.flashcard_ids_to_add:
            min_level_stmt = select(func.min(FlashcardPollItem.leitner_level)).where(
                FlashcardPollItem.user_id == poll.user_id.value
            )
            min_level_result = await session.execute(min_level_stmt)
            min_level = min_level_result.scalar() or 0

            for f_id in poll.flashcard_ids_to_add:
                insert_data.append(
                    FlashcardPollItem(
                        user_id=poll.user_id.value,
                        flashcard_id=f_id.value,
                        easy_ratings_count=0,
                        easy_ratings_count_to_purge=poll.get_easy_repetitions_count_to_purge(),
                        leitner_level=min_level,
                    )
                )

            session.add_all(insert_data)

        await session.commit()

    async def select_next_leitner_flashcard(
        self, user_id: UserId, exclude_flashcard_ids: List[FlashcardId], limit: int
    ) -> List[FlashcardId]:
        session: AsyncSession = get_session()
        stmt = (
            select(FlashcardPollItem)
            .where(FlashcardPollItem.user_id == user_id.value)
            .where(~FlashcardPollItem.flashcard_id.in_([f.value for f in exclude_flashcard_ids]))
            .order_by(FlashcardPollItem.leitner_level, FlashcardPollItem.updated_at)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [FlashcardId(item.flashcard_id) for item in result.scalars().all()]

    async def reset_leitner_level_if_max_level_exceeded(
        self, user_id: UserId, max_level: int
    ) -> None:
        session: AsyncSession = get_session()
        stmt = select(func.max(FlashcardPollItem.leitner_level)).where(
            FlashcardPollItem.user_id == user_id.value
        )
        result = await session.execute(stmt)
        current_max = result.scalar() or 0
        if current_max > max_level:
            await session.execute(
                update(FlashcardPollItem)
                .where(FlashcardPollItem.user_id == user_id.value)
                .values(leitner_level=0)
            )
            await session.commit()

    async def delete_all_by_user_id(self, user_id: UserId) -> None:
        session: AsyncSession = get_session()
        await session.execute(
            delete(FlashcardPollItem).where(FlashcardPollItem.user_id == user_id.value)
        )
        await session.commit()
