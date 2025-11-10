from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, or_, text, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import SmTwoFlashcards as SmTwoFlashcardsTable
from src.flashcard.application.repository.contracts import (
    FlashcardSortCriteria,
    ISmTwoFlashcardRepository,
)
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.models.sm_two_flashcard import SmTwoFlashcard
from src.flashcard.domain.models.sm_two_flashcards import SmTwoFlashcards
from src.flashcard.domain.value_objects import FlashcardId, OwnerId
from src.flashcard.infrastructure.repository.sm_two.criteria_factory import (
    FlashcardSortCriteriaFactory,
)
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.enum import FlashcardOwnerType, Rating

from core.models import (
    Flashcards as FlashcardsTable,
    SmTwoFlashcards as SmTwoTable,
    FlashcardDecks as DecksTable,
    FlashcardPollItems as FlashcardPollItemsTable,
)
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.shared.enum import LanguageLevel, Language
from src.shared.value_objects.language import Language as LanguageVO
from src.shared.models import Emoji
from decimal import Decimal


class SmTwoFlashcardRepository(ISmTwoFlashcardRepository):
    def __init__(self, criteria_factory: FlashcardSortCriteriaFactory, session: AsyncSession):
        self.criteria_factory = criteria_factory
        self.session = session

    async def reset_repetitions_in_session(self, user_id: UserId) -> None:
        await self.session.execute(
            update(SmTwoFlashcardsTable)
            .where(SmTwoFlashcardsTable.user_id == user_id.value)
            .where(SmTwoFlashcardsTable.repetitions_in_session > 0)
            .values(repetitions_in_session=0)
        )
        await self.session.commit()

    async def find_many(self, user_id: UserId, flashcard_ids: List[FlashcardId]) -> SmTwoFlashcards:
        query = (
            select(SmTwoFlashcardsTable)
            .where(SmTwoFlashcardsTable.user_id == user_id.value)
            .where(SmTwoFlashcardsTable.flashcard_id.in_([f.value for f in flashcard_ids]))
        )
        result = await self.session.execute(query)
        rows = result.scalars().all()
        mapped = [self._map_sm_two(row) for row in rows]
        return SmTwoFlashcards(sm_two_flashcards=mapped)

    from decimal import Decimal

    async def save_many(self, sm_two_flashcards: SmTwoFlashcards) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        for flashcard in sm_two_flashcards.all():
            stmt = (
                select(SmTwoFlashcardsTable)
                .where(SmTwoFlashcardsTable.flashcard_id == flashcard.flashcard_id.value)
                .where(SmTwoFlashcardsTable.user_id == flashcard.user_id.value)
            )
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            # Konwertujemy float na Decimal przed zapisem
            repetition_ratio = Decimal(str(flashcard.repetition_ratio))
            repetition_interval = Decimal(str(min(flashcard.repetition_interval, 9999)))

            if existing is None:
                await self.session.execute(
                    insert(SmTwoFlashcardsTable).values(
                        flashcard_id=flashcard.flashcard_id.value,
                        user_id=flashcard.user_id.value,
                        repetition_ratio=repetition_ratio,
                        repetition_interval=repetition_interval,
                        repetition_count=flashcard.repetition_count,
                        min_rating=flashcard.min_rating,
                        repetitions_in_session=flashcard.repetitions_in_session,
                        last_rating=flashcard.rating.value if flashcard.rating else None,
                        created_at=now,
                        updated_at=now,
                    )
                )
            else:
                await self.session.execute(
                    update(SmTwoFlashcardsTable)
                    .where(SmTwoFlashcardsTable.flashcard_id == flashcard.flashcard_id.value)
                    .where(SmTwoFlashcardsTable.user_id == flashcard.user_id.value)
                    .values(
                        repetition_ratio=repetition_ratio,
                        repetition_interval=repetition_interval,
                        repetition_count=flashcard.repetition_count,
                        min_rating=flashcard.min_rating,
                        repetitions_in_session=flashcard.repetitions_in_session,
                        last_rating=flashcard.rating.value if flashcard.rating else None,
                        updated_at=now,
                    )
                )

        await self.session.commit()

    async def get_next_flashcards(
        self,
        user_id: UserId,
        limit: int,
        exclude_flashcard_ids: List[FlashcardId],
        sort_criteria: List[FlashcardSortCriteria],
        cards_per_session: int,
        from_poll: bool,
        exclude_from_poll: bool,
        front: Language,
        back: Language,
        deck_id: Optional[FlashcardDeckId] = None,
    ) -> List[Flashcard]:
        flashcard_limit = max(3, int(0.1 * cards_per_session))

        sort_sql = [self.criteria_factory.make(s).apply() for s in sort_criteria]

        query = select(
            FlashcardsTable,
            DecksTable.id.label("deck_id"),
            DecksTable.user_id.label("deck_user_id"),
            DecksTable.admin_id.label("deck_admin_id"),
            DecksTable.tag.label("deck_tag"),
            DecksTable.name.label("deck_name"),
            DecksTable.default_language_level.label("deck_default_language_level"),
            SmTwoTable.last_rating.label("sm_last_rating"),
            SmTwoTable.repetitions_in_session.label("sm_repetitions_in_session"),
        )

        if from_poll:
            query = (
                query.select_from(FlashcardPollItemsTable)
                .where(FlashcardPollItemsTable.user_id == user_id.value)
                .join(FlashcardsTable, FlashcardsTable.id == FlashcardPollItemsTable.flashcard_id)
            )

        query = query.outerjoin(DecksTable, DecksTable.id == FlashcardsTable.flashcard_deck_id)

        query = query.outerjoin(
            SmTwoTable,
            (SmTwoTable.flashcard_id == FlashcardsTable.id) & (SmTwoTable.user_id == user_id.value),
        )

        query = query.where(
            FlashcardsTable.front_lang == front.value,
            FlashcardsTable.back_lang == back.value,
        )

        if deck_id:
            query = query.where(FlashcardsTable.flashcard_deck_id == deck_id.get_value())

        if exclude_from_poll:
            subquery = select(FlashcardPollItemsTable.flashcard_id).where(
                FlashcardPollItemsTable.user_id == user_id.value
            )
            query = query.where(~FlashcardsTable.id.in_(subquery))

        if exclude_flashcard_ids:
            query = query.where(~FlashcardsTable.id.in_([f.value for f in exclude_flashcard_ids]))

        query = query.where(
            or_(FlashcardsTable.user_id == user_id.value, FlashcardsTable.user_id.is_(None))
        )

        # Order clause
        order_by_clause = [
            text(
                f"CASE WHEN COALESCE(sm_two_flashcards.repetitions_in_session, 0) < {flashcard_limit} THEN 1 ELSE 0 END DESC"
            )
        ]
        order_by_clause += [text(sql) for sql in sort_sql]

        query = query.limit(limit).order_by(*order_by_clause)

        result = await self.session.execute(query)
        rows = result.all()

        # Map rows to Flashcard domain objects
        flashcards = []
        for row in rows:
            flashcards.append(self._map(row))
        return flashcards

    def _map(self, row) -> Flashcard:
        flashcard_row = row.Flashcards

        # Map deck if present
        deck = None
        if row.deck_id is not None:
            deck = Deck(
                owner=self.build_owner(row.deck_user_id, row.deck_admin_id),
                tag=row.deck_tag,
                name=row.deck_name,
                default_language_level=LanguageLevel(row.deck_default_language_level),
            )
            deck.id = FlashcardDeckId(row.deck_id)

        last_rating = Rating(row.sm_last_rating) if row.sm_last_rating is not None else None

        return Flashcard(
            id=FlashcardId(flashcard_row.id),
            front_word=flashcard_row.front_word,
            front_lang=LanguageVO(flashcard_row.front_lang),
            back_word=flashcard_row.back_word,
            back_lang=LanguageVO(flashcard_row.back_lang),
            front_context=flashcard_row.front_context,
            back_context=flashcard_row.back_context,
            owner=self.build_owner(flashcard_row.user_id, flashcard_row.admin_id),
            deck=deck,
            level=LanguageLevel(flashcard_row.language_level),
            emoji=Emoji.from_unicode(flashcard_row.emoji) if flashcard_row.emoji else None,
            last_user_rating=last_rating,
        )

    def build_owner(self, user_id: Optional[str], admin_id: Optional[str]) -> Owner:
        """
        Build an Owner domain object based on user_id or admin_id.
        Raises ValueError if both are None.
        """
        if user_id:
            return Owner(id=OwnerId(value=user_id), flashcard_owner_type=FlashcardOwnerType.USER)
        if admin_id:
            return Owner(id=OwnerId(value=admin_id), flashcard_owner_type=FlashcardOwnerType.ADMIN)

        raise ValueError("user_id and admin_id cannot be both null")

    def _map_sm_two(self, row: SmTwoFlashcardsTable) -> SmTwoFlashcard:
        return SmTwoFlashcard(
            user_id=UserId(row.user_id),
            flashcard_id=FlashcardId(row.flashcard_id),
            repetition_ratio=float(row.repetition_ratio),
            repetition_interval=float(row.repetition_interval),
            repetition_count=row.repetition_count,
            min_rating=row.min_rating,
            repetitions_in_session=row.repetitions_in_session,
            rating=Rating(row.last_rating) if row.last_rating is not None else None,
        )
