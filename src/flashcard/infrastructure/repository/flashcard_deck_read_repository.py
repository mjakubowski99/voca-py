from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from core.models import FlashcardDecks, Flashcards, LearningSessionFlashcards, LearningSessions
from src.flashcard.application.dto import owner_deck_read
from src.flashcard.application.dto.deck_details_read import DeckDetailsRead
from src.flashcard.application.repository.contracts import IFlashcardDeckReadRepository
from src.flashcard.domain.enum import FlashcardOwnerType, Rating
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardDeckId, OwnerId
from src.flashcard.infrastructure.repository.flashcard_read_repository import (
    FlashcardReadRepository,
)
from src.shared.enum import Language, LanguageLevel
from src.shared.value_objects.user_id import UserId
from core.db import get_session
from src.flashcard.application.dto.owner_deck_read import OwnerDeckRead


class FlashcardDeckReadRepository(IFlashcardDeckReadRepository):
    def __init__(self, flashcard_repository: FlashcardReadRepository):
        self.flashcard_repository = flashcard_repository

    async def find_details(
        self,
        user_id: UserId,
        flashcard_deck_id: FlashcardDeckId,
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> DeckDetailsRead:
        deck = await self._find_deck(flashcard_deck_id, user_id)

        flashcards = await self.flashcard_repository.search(
            user_id, None, None, flashcard_deck_id, None, search, page, per_page
        )

        count = await self.flashcard_repository.get_count_in_deck(flashcard_deck_id)

        total_avg_rating = await self.get_rating_stats([flashcard_deck_id.value], user_id, 2)

        if count:
            avg_rating = (
                float(total_avg_rating[flashcard_deck_id.value])
                / (count * Rating.max_rating())
                * 100.0
            )
        else:
            avg_rating = 0.0

        return DeckDetailsRead(
            id=FlashcardDeckId(value=deck.id),
            name=deck.name,
            flashcards=flashcards,
            page=page,
            per_page=per_page,
            count=count,
            owner_type=self._build_owner(deck).flashcard_owner_type,
            language_level=deck.most_frequent_language_level
            if deck.most_frequent_language_level
            else deck.default_language_level,
            last_learnt_at=deck.last_learnt_at,
            rating_percentage=avg_rating,
        )

    async def _find_deck(
        self, deck_id: FlashcardDeckId, user_id: UserId
    ) -> Optional[FlashcardDecks]:
        most_freq_lvl_subq = (
            select(Flashcards.language_level)
            .filter(Flashcards.flashcard_deck_id == deck_id.value)
            .group_by(Flashcards.language_level)
            .order_by(desc(func.count(Flashcards.id)))
            .limit(1)
            .scalar_subquery()
        )

        last_learnt_subq = (
            select(func.max(LearningSessionFlashcards.updated_at))
            .join(Flashcards, LearningSessionFlashcards.flashcard_id == Flashcards.id)
            .join(
                LearningSessions,
                LearningSessionFlashcards.learning_session_id == LearningSessions.id,
            )
            .filter(
                Flashcards.flashcard_deck_id == deck_id.value,
                LearningSessions.user_id == user_id.value,
            )
            .scalar_subquery()
        )

        query = select(
            FlashcardDecks,
            most_freq_lvl_subq.label("most_frequent_language_level"),
            last_learnt_subq.label("last_learnt_at"),
        ).filter(FlashcardDecks.id == deck_id.value)

        result = await get_session().execute(query)
        deck_row = result.first()
        if not deck_row:
            return None

        deck, most_frequent_language_level, last_learnt_at = deck_row
        deck.most_frequent_language_level = most_frequent_language_level
        deck.last_learnt_at = last_learnt_at
        return deck

    async def get_rating_stats(
        self, deck_ids: List[int], user_id: UserId, ratings_limit: int = 2
    ) -> Dict[str, float]:
        subq = (
            select(
                LearningSessionFlashcards.flashcard_id.label("flashcard_id"),
                LearningSessionFlashcards.rating.label("rating"),
                func.row_number()
                .over(
                    partition_by=LearningSessionFlashcards.flashcard_id,
                    order_by=desc(LearningSessionFlashcards.id),
                )
                .label("rn"),
            )
            .join(
                LearningSessions,
                LearningSessions.id == LearningSessionFlashcards.learning_session_id,
            )
            .filter(LearningSessions.user_id == user_id.value)
            .subquery()
        )

        avg_ratings_subq = (
            select(subq.c.flashcard_id, func.avg(subq.c.rating).label("avg_rating"))
            .where(subq.c.rn <= ratings_limit)
            .group_by(subq.c.flashcard_id)
            .subquery()
        )

        query = (
            select(
                Flashcards.flashcard_deck_id,
                func.coalesce(func.sum(avg_ratings_subq.c.avg_rating), 0).label("total_avg_rating"),
            )
            .join(avg_ratings_subq, avg_ratings_subq.c.flashcard_id == Flashcards.id, isouter=True)
            .filter(Flashcards.flashcard_deck_id.in_(deck_ids))
            .group_by(Flashcards.flashcard_deck_id)
        )

        result = await get_session().execute(query)
        rows = result.all()

        return {row.flashcard_deck_id: row.total_avg_rating for row in rows}

    def _build_owner(self, deck: FlashcardDecks) -> Owner:
        return Owner(
            id=OwnerId(value=deck.user_id if deck.user_id is not None else deck.admin_id),
            flashcard_owner_type=FlashcardOwnerType.USER
            if deck.user_id is not None
            else FlashcardOwnerType.ADMIN,
        )

    async def get_admin_decks(
        self,
        user_id: UserId,
        front_lang: Language,
        back_lang: Language,
        level: Optional[LanguageLevel],
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> list[OwnerDeckRead]:
        """
        Equivalent of PHP getAdminDecks()
        """
        async with get_session() as session:
            # Subqueries for most frequent language level
            most_freq_lvl_subq = (
                select(Flashcards.flashcard_deck_id, Flashcards.language_level)
                .filter(Flashcards.front_lang == front_lang.value)
                .filter(Flashcards.back_lang == back_lang.value)
                .group_by(Flashcards.flashcard_deck_id, Flashcards.language_level)
                .order_by(desc(func.count(Flashcards.id)))
                .limit(1)
                .subquery()
            )

            # Subquery for flashcards count
            flashcards_count_subq = (
                select(
                    Flashcards.flashcard_deck_id,
                    func.count(Flashcards.id).label("flashcards_count"),
                )
                .group_by(Flashcards.flashcard_deck_id)
                .subquery()
            )

            # Subquery for last learnt
            last_learnt_subq = (
                select(
                    Flashcards.flashcard_deck_id,
                    func.max(LearningSessionFlashcards.updated_at).label("last_learnt_at"),
                )
                .join(
                    LearningSessions,
                    LearningSessions.id == LearningSessionFlashcards.learning_session_id,
                )
                .join(Flashcards, Flashcards.id == LearningSessionFlashcards.flashcard_id)
                .filter(LearningSessions.user_id == user_id.value)
                .group_by(Flashcards.flashcard_deck_id)
                .subquery()
            )

            # Base query
            query = (
                select(
                    FlashcardDecks,
                    flashcards_count_subq.c.flashcards_count,
                    last_learnt_subq.c.last_learnt_at,
                    most_freq_lvl_subq.c.language_level.label("most_frequent_language_level"),
                )
                .join(
                    flashcards_count_subq,
                    flashcards_count_subq.c.flashcard_deck_id == FlashcardDecks.id,
                    isouter=True,
                )
                .join(
                    last_learnt_subq,
                    last_learnt_subq.c.flashcard_deck_id == FlashcardDecks.id,
                    isouter=True,
                )
                .join(
                    most_freq_lvl_subq,
                    most_freq_lvl_subq.c.flashcard_deck_id == FlashcardDecks.id,
                    isouter=True,
                )
                .filter(
                    FlashcardDecks.admin_id.isnot(None),
                    FlashcardDecks.user_id.is_(None),
                )
            )

            if level:
                query = query.filter(FlashcardDecks.default_language_level == level.value)
            if search:
                query = query.filter(func.lower(FlashcardDecks.name).like(f"%{search.lower()}%"))

            query = query.order_by(desc(FlashcardDecks.created_at), FlashcardDecks.name.asc())
            query = query.limit(per_page).offset((page - 1) * per_page)

            result = await session.execute(query)
            rows = result.all()

            rating_stats = await self.get_rating_stats(
                [row.FlashcardDecks.id for row in rows], user_id
            )

            decks: list[owner_deck_read] = []
            for row in rows:
                deck = row.FlashcardDecks
                total_avg = rating_stats.get(deck.id, 0.0)
                avg_rating = (
                    (total_avg / (row.flashcards_count * Rating.max_rating()) * 100.0)
                    if row.flashcards_count
                    else 0.0
                )
                decks.append(
                    OwnerDeckRead(
                        id=FlashcardDeckId(deck.id),
                        name=deck.name,
                        language_level=row.most_frequent_language_level
                        or deck.default_language_level,
                        flashcards_count=row.flashcards_count or 0,
                        rating_percentage=avg_rating,
                        last_learnt_at=row.last_learnt_at,
                        owner_type=FlashcardOwnerType.ADMIN,
                    )
                )

            return decks

    async def get_by_user(
        self,
        user_id: UserId,
        front_lang: Language,
        back_lang: Language,
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> list[OwnerDeckRead]:
        """
        Equivalent of PHP getByUser()
        """
        async with get_session() as session:
            most_freq_lvl_subq = (
                select(Flashcards.flashcard_deck_id, Flashcards.language_level)
                .filter(Flashcards.front_lang == front_lang.value)
                .filter(Flashcards.back_lang == back_lang.value)
                .group_by(Flashcards.flashcard_deck_id, Flashcards.language_level)
                .order_by(desc(func.count(Flashcards.id)))
                .limit(1)
                .subquery()
            )

            flashcards_count_subq = (
                select(
                    Flashcards.flashcard_deck_id,
                    func.count(Flashcards.id).label("flashcards_count"),
                )
                .group_by(Flashcards.flashcard_deck_id)
                .subquery()
            )

            last_learnt_subq = (
                select(
                    Flashcards.flashcard_deck_id,
                    func.max(LearningSessionFlashcards.updated_at).label("last_learnt_at"),
                )
                .join(
                    LearningSessions,
                    LearningSessions.id == LearningSessionFlashcards.learning_session_id,
                )
                .join(Flashcards, Flashcards.id == LearningSessionFlashcards.flashcard_id)
                .filter(LearningSessions.user_id == user_id.value)
                .group_by(Flashcards.flashcard_deck_id)
                .subquery()
            )

            query = (
                select(
                    FlashcardDecks,
                    flashcards_count_subq.c.flashcards_count,
                    last_learnt_subq.c.last_learnt_at,
                    most_freq_lvl_subq.c.language_level.label("most_frequent_language_level"),
                )
                .join(
                    flashcards_count_subq,
                    flashcards_count_subq.c.flashcard_deck_id == FlashcardDecks.id,
                    isouter=True,
                )
                .join(
                    last_learnt_subq,
                    last_learnt_subq.c.flashcard_deck_id == FlashcardDecks.id,
                    isouter=True,
                )
                .join(
                    most_freq_lvl_subq,
                    most_freq_lvl_subq.c.flashcard_deck_id == FlashcardDecks.id,
                    isouter=True,
                )
                .filter(
                    FlashcardDecks.user_id == user_id.value,
                    FlashcardDecks.admin_id.is_(None),
                )
            )

            if search:
                query = query.filter(func.lower(FlashcardDecks.name).like(f"%{search.lower()}%"))

            query = query.order_by(desc(FlashcardDecks.created_at))
            query = query.limit(per_page).offset((page - 1) * per_page)

            result = await session.execute(query)
            rows = result.all()

            rating_stats = await self.get_rating_stats(
                [row.FlashcardDecks.id for row in rows], user_id
            )

            decks: list[OwnerDeckRead] = []
            for row in rows:
                deck = row.FlashcardDecks
                total_avg = rating_stats.get(deck.id, 0.0)
                avg_rating = (
                    (total_avg / (row.flashcards_count * Rating.max_rating()) * 100.0)
                    if row.flashcards_count
                    else 0.0
                )
                decks.append(
                    OwnerDeckRead(
                        id=FlashcardDeckId(deck.id),
                        name=deck.name,
                        language_level=row.most_frequent_language_level
                        or deck.default_language_level,
                        flashcards_count=row.flashcards_count or 0,
                        rating_percentage=avg_rating,
                        last_learnt_at=row.last_learnt_at,
                        owner_type=FlashcardOwnerType.USER,
                    )
                )

            return decks
