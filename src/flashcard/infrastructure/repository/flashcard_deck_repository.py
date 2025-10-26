from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.db import get_session
from core.models import FlashcardDecks, FlashcardDeckActivities
from src.flashcard.domain.enum import FlashcardOwnerType
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.value_objects import FlashcardDeckId, OwnerId
from src.flashcard.application.repository.contracts import IFlashcardDeckRepository
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language


class FlashcardDeckRepository(IFlashcardDeckRepository):
    async def create(self, deck: Deck) -> FlashcardDeckId:
        session: AsyncSession = get_session()
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        db_deck = FlashcardDecks(
            name=deck.name,
            tag=deck.name,
            user_id=deck.owner.id.value if deck.owner.is_user() else None,
            admin_id=deck.owner.id.value if deck.owner.is_admin() else None,
            default_language_level=deck.default_language_level.value,
            created_at=now,
            updated_at=now,
        )
        session.add(db_deck)
        await session.flush()
        await session.refresh(db_deck)
        return FlashcardDeckId(db_deck.id)

    async def find_by_id(self, deck_id: FlashcardDeckId) -> Deck:
        session: AsyncSession = get_session()
        result = await session.execute(
            select(FlashcardDecks).where(FlashcardDecks.id == deck_id.value)
        )
        db_deck = result.scalar_one_or_none()
        if not db_deck:
            raise ValueError("Deck not found")
        return self._map(db_deck)

    async def search_by_name(
        self, user_id: UserId, name: str, front_lang: Language, back_lang: Language
    ) -> Optional[Deck]:
        session: AsyncSession = get_session()
        query = select(FlashcardDecks).where(
            FlashcardDecks.user_id == user_id.value,
            FlashcardDecks.name == name,
        )
        result = await session.execute(query)
        db_deck = result.scalar_one_or_none()
        return self._map(db_deck) if db_deck else None

    async def search_by_name_admin(
        self, name: str, front_lang: Language, back_lang: Language
    ) -> Optional[Deck]:
        session: AsyncSession = get_session()
        query = select(FlashcardDecks).where(
            FlashcardDecks.admin_id.isnot(None),
            FlashcardDecks.name == name,
        )
        result = await session.execute(query)
        db_deck = result.scalar_one_or_none()
        return self._map(db_deck) if db_deck else None

    async def update(self, deck: Deck) -> None:
        session: AsyncSession = get_session()
        now = datetime.now(timezone.utc)
        await session.execute(
            update(FlashcardDecks)
            .where(FlashcardDecks.id == deck.id.value)
            .values(
                user_id=deck.owner.id.value if deck.owner.is_user() else None,
                admin_id=deck.owner.id.value if deck.owner.is_admin() else None,
                tag=deck.name,
                name=deck.name,
                default_language_level=deck.default_language_level.value,
                updated_at=now,
            )
        )
        await session.commit()

    async def update_last_viewed_at(self, deck_id: FlashcardDeckId, user_id: UserId):
        session: AsyncSession = get_session()
        now = datetime.now(timezone.utc)
        stmt = (
            pg_insert(FlashcardDeckActivities)
            .values(
                user_id=user_id.value,
                flashcard_deck_id=deck_id.value,
                last_viewed_at=now,
            )
            .on_conflict_do_update(
                index_elements=["user_id", "flashcard_deck_id"],
                set_={"last_viewed_at": now},
            )
        )
        await session.execute(stmt)
        await session.commit()

    async def get_by_user(
        self, user_id: UserId, front_lang: Language, back_lang: Language, page: int, per_page: int
    ) -> List[Deck]:
        session: AsyncSession = get_session()
        offset = (page - 1) * per_page
        query = (
            select(FlashcardDecks)
            .where(FlashcardDecks.user_id == user_id.value)
            .offset(offset)
            .limit(per_page)
        )
        result = await session.execute(query)
        decks = result.scalars().all()
        return [self._map(d) for d in decks]

    async def remove(self, deck: Deck) -> None:
        session: AsyncSession = get_session()
        await session.execute(delete(FlashcardDecks).where(FlashcardDecks.id == deck.id.value))
        await session.commit()

    async def delete_all_for_user(self, user_id: UserId) -> None:
        session: AsyncSession = get_session()
        await session.execute(delete(FlashcardDecks).where(FlashcardDecks.user_id == user_id.value))
        await session.commit()

    async def bulk_delete(self, user_id: UserId, deck_ids: List[FlashcardDeckId]) -> None:
        session: AsyncSession = get_session()
        await session.execute(
            delete(FlashcardDecks).where(
                FlashcardDecks.user_id == user_id.value,
                FlashcardDecks.id.in_([d.value for d in deck_ids]),
            )
        )
        await session.commit()

    def _map(self, db_deck: FlashcardDecks) -> Deck:
        from src.flashcard.domain.models.owner import Owner
        from src.shared.enum import LanguageLevel

        deck = Deck(
            owner=Owner(
                id=OwnerId(value=db_deck.user_id), flashcard_owner_type=FlashcardOwnerType.USER
            )
            if db_deck.user_id
            else Owner(
                id=OwnerId(value=db_deck.admin_id), flashcard_owner_type=FlashcardOwnerType.ADMIN
            ),
            tag=db_deck.tag,
            name=db_deck.name,
            default_language_level=LanguageLevel(db_deck.default_language_level),
        )
        deck.id = FlashcardDeckId(db_deck.id)
        return deck
