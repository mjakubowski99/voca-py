from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql import text
from src.shared.models import Emoji
from src.flashcard.domain.enum import FlashcardOwnerType, GeneralRatingType
from src.flashcard.domain.value_objects import FlashcardId, FlashcardDeckId
from src.flashcard.application.dto.flashcard_read import FlashcardRead
from src.flashcard.application.dto.general_rating import GeneralRating
from src.shared.enum import LanguageLevel
from src.shared.value_objects.language import Language
from core.models import Flashcards as FlashcardDB, LearningSessionFlashcards, LearningSessions
from src.shared.value_objects.user_id import UserId


class FlashcardReadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_flashcard_stats(
        self,
        front_lang: Language,
        back_lang: Language,
        deck_id: Optional[FlashcardDeckId] = None,
        user_id: Optional[int] = None,
        flashcard_owner_type: Optional[FlashcardOwnerType] = None,
    ) -> List[dict]:
        query = select(
            FlashcardDB.rating, func.count(FlashcardDB.rating).label("rating_count")
        ).select_from(self.session.query(FlashcardDB))

        # Filtry językowe
        query = query.where(FlashcardDB.front_lang == front_lang.value)
        query = query.where(FlashcardDB.back_lang == back_lang.value)

        # Filtry właściciela
        if flashcard_owner_type == FlashcardOwnerType.USER:
            query = query.where(FlashcardDB.user_id.isnot(None))
        elif flashcard_owner_type == FlashcardOwnerType.ADMIN:
            query = query.where(FlashcardDB.admin_id.isnot(None))

        # Filtr deck
        if deck_id is not None:
            query = query.where(FlashcardDB.flashcard_deck_id == deck_id.value)

        # Dołączamy sesje użytkownika jeśli user_id podany
        if user_id is not None:
            query = (
                query.join(
                    LearningSessionFlashcards,
                    LearningSessionFlashcards.flashcard_id == FlashcardDB.id,
                    isouter=True,
                )
                .join(
                    LearningSessions,
                    LearningSessions.id == LearningSessionFlashcards.learning_session_id,
                    isouter=True,
                )
                .where(LearningSessions.user_id == user_id)
            )

        query = query.where(FlashcardDB.rating.isnot(None))
        query = query.group_by(FlashcardDB.rating)

        result = await self.session.execute(query)
        rows = result.all()

        total_count = sum(row.rating_count for row in rows)

        # Generowanie statystyk w stylu RatingStatsRead
        ratings_data = []
        for rating in range(1, 6):  # assuming 1-5 ratings
            row = next((r for r in rows if r.rating == rating), None)
            count = row.rating_count if row else 0
            ratings_data.append(
                {
                    "rating": rating,
                    "percentage": 0.0 if total_count == 0 else count / total_count * 100,
                }
            )

        return ratings_data

    async def get_by_user(
        self,
        user_id: int,
        front_lang: Language,
        back_lang: Language,
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> dict:
        flashcards = await self.search(user_id, front_lang, back_lang, search, page, per_page)

        count_stmt = select(func.count()).where(FlashcardDB.user_id == user_id)
        result = await self.session.execute(count_stmt)
        total_count = result.scalar_one()

        return {
            "user_id": user_id,
            "flashcards": flashcards,
            "page": page,
            "per_page": per_page,
            "total_count": total_count,
        }

    async def get_count_in_deck(self, deck_id: FlashcardDeckId) -> int:
        stmt = select(func.count()).where(FlashcardDB.flashcard_deck_id == deck_id.value)

        result = await self.session.execute(stmt)
        count = result.scalar_one()  # returns int

        return count

    async def search(
        self,
        user_id: UserId,  # the current user (used in subqueries)
        front_lang: Optional[Language] = None,
        back_lang: Optional[Language] = None,
        deck_id: Optional[FlashcardDeckId] = None,
        user_filter: Optional[UserId] = None,  # optional owner filter (like $user_filter in PHP)
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> List[FlashcardRead]:
        rating_max = 5  # replace with Rating::maxRating() equivalent if dynamic
        offset = (page - 1) * per_page

        sql = """
        SELECT
            f.*,
            (
                SELECT lsf.rating
                FROM learning_session_flashcards AS lsf
                INNER JOIN learning_sessions AS ls
                    ON ls.id = lsf.learning_session_id
                WHERE f.id = lsf.flashcard_id
                  AND lsf.rating IS NOT NULL
                  AND ls.user_id = :current_user_id
                ORDER BY lsf.updated_at DESC
                LIMIT 1
            ) AS last_rating,
            (
                SELECT AVG(COALESCE(lsf.rating, 0) / CAST(:rating_max AS FLOAT))
                FROM learning_session_flashcards AS lsf
                INNER JOIN learning_sessions AS ls
                    ON ls.id = lsf.learning_session_id
                WHERE f.id = lsf.flashcard_id
                  AND ls.user_id = :current_user_id
            ) AS rating_ratio
        FROM flashcards AS f
        WHERE 1 = 1
        """

        params = {
            "current_user_id": user_id.value,
            "rating_max": rating_max,
            "limit": per_page,
            "offset": offset,
        }

        # filters
        if front_lang is not None:
            sql += " AND f.front_lang = :front_lang"
            params["front_lang"] = front_lang.value

        if back_lang is not None:
            sql += " AND f.back_lang = :back_lang"
            params["back_lang"] = back_lang.value

        if deck_id is not None:
            sql += " AND f.flashcard_deck_id = :deck_id"
            params["deck_id"] = deck_id.value

        if user_filter is not None:
            sql += " AND f.user_id = :user_filter"
            params["user_filter"] = user_filter.value

        if search is not None:
            # mirror PHP's LOWER(...) LIKE '%...%'
            sql += " AND (LOWER(f.front_word) LIKE :search OR LOWER(f.back_word) LIKE :search)"
            params["search"] = f"%{search.lower()}%"

        sql += " ORDER BY f.front_word ASC LIMIT :limit OFFSET :offset"

        result = await self.session.execute(text(sql), params)
        rows = result.mappings().all()  # dict-like rows

        flashcards: List[FlashcardRead] = []
        for row in rows:
            flashcards.append(
                FlashcardRead(
                    id=FlashcardId(row["id"]),
                    front_word=row["front_word"],
                    front_lang=Language.from_string(row["front_lang"]),
                    back_word=row["back_word"],
                    back_lang=Language.from_string(row["back_lang"]),
                    front_context=row.get("front_context"),
                    back_context=row.get("back_context"),
                    general_rating=GeneralRating(value=row.get("last_rating"))
                    if row.get("last_rating")
                    else GeneralRating(value=GeneralRatingType.UNKNOWN),
                    language_level=LanguageLevel(row["language_level"])
                    if row.get("language_level") is not None
                    else None,
                    rating_percentage=(row.get("rating_ratio") or 0.0) * 100.0,
                    emoji=Emoji.from_unicode(row["emoji"]) if row.get("emoji") else None,
                    owner_type=FlashcardOwnerType.USER
                    if row.get("user_id")
                    else FlashcardOwnerType.ADMIN,
                )
            )

        return flashcards
