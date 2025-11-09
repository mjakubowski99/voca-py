from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import insert
from core.models import Flashcards, FlashcardDecks
from src.flashcard.application.repository.contracts import IFlashcardRepository
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardId, FlashcardDeckId
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language
from src.shared.enum import LanguageLevel
from src.shared.models import Emoji
from src.flashcard.domain.models.story_collection import StoryCollection
from core.db import get_session


class FlashcardRepository(IFlashcardRepository):
    async def get_by_category(self, deck_id: FlashcardDeckId) -> list[Flashcard]:
        session: AsyncSession = get_session()
        stmt = (
            select(Flashcards, FlashcardDecks)
            .join(FlashcardDecks, Flashcards.flashcard_deck_id == FlashcardDecks.id)
            .where(Flashcards.flashcard_deck_id == deck_id.value)
        )
        result = await session.execute(stmt)
        return [self.map(row[0], row[1]) for row in result.fetchall()]

    async def get_random_flashcards(
        self, user_id: UserId, limit: int, exclude_ids: list[FlashcardId]
    ) -> list[Flashcard]:
        session: AsyncSession = get_session()
        stmt = (
            select(Flashcards, FlashcardDecks)
            .join(FlashcardDecks, Flashcards.flashcard_deck_id == FlashcardDecks.id)
            .where(
                ((Flashcards.user_id == user_id.value) | (Flashcards.admin_id == user_id.value)),
                ~Flashcards.id.in_([f.value for f in exclude_ids]),
            )
            .order_by(func.random())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [self.map(row[0], row[1]) for row in result.fetchall()]

    async def get_random_flashcards_by_category(
        self, deck_id: FlashcardDeckId, limit: int, exclude_ids: list[FlashcardId]
    ) -> list[Flashcard]:
        session: AsyncSession = get_session()
        stmt = (
            select(Flashcards, FlashcardDecks)
            .join(FlashcardDecks, Flashcards.flashcard_deck_id == FlashcardDecks.id)
            .where(
                Flashcards.flashcard_deck_id == deck_id.value,
                ~Flashcards.id.in_([f.value for f in exclude_ids]),
            )
            .order_by(func.random())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return [self.map(row[0], row[1]) for row in result.fetchall()]

    async def create_many(self, flashcards: list[Flashcard]) -> None:
        session: AsyncSession = get_session()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        insert_data = [
            {
                "user_id": f.owner.id.value if f.owner.is_user() else None,
                "admin_id": f.owner.id.value if f.owner.is_admin() else None,
                "flashcard_deck_id": f.deck.id.value,
                "front_word": f.front_word,
                "front_lang": f.front_lang.get_value(),
                "back_word": f.back_word,
                "back_lang": f.back_lang.get_value(),
                "front_context": f.front_context,
                "back_context": f.back_context,
                "language_level": f.level.value,
                "emoji": f.emoji.to_unicode() if f.emoji else None,
                "created_at": now,
                "updated_at": now,
            }
            for f in flashcards
        ]
        await session.execute(Flashcards.__table__.insert(), insert_data)
        await session.commit()

    async def create_many_from_story_flashcards(self, stories: StoryCollection) -> StoryCollection:
        """
        Inserts all flashcards from a StoryCollection in bulk, assigns IDs to each,
        and returns the updated StoryCollection.
        """
        session: AsyncSession = get_session()
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        insert_data = []
        for i, story_flashcard in enumerate(stories.get_all_story_flashcards()):
            f = story_flashcard.flashcard
            insert_data.append(
                {
                    "user_id": f.owner.id.value if f.owner.is_user() else None,
                    "admin_id": f.owner.id.value if f.owner.is_admin() else None,
                    "flashcard_deck_id": f.deck.id.value,
                    "front_word": f.front_word,
                    "front_lang": f.front_lang.get_value(),
                    "back_word": f.back_word,
                    "back_lang": f.back_lang.get_value(),
                    "front_context": f.front_context,
                    "back_context": f.back_context,
                    "language_level": f.level.value,
                    "emoji": f.emoji.to_unicode() if f.emoji else None,
                    "created_at": now + timedelta(seconds=i),
                    "updated_at": now + timedelta(seconds=i),
                }
            )

        stmt = insert(Flashcards).returning(Flashcards.id).values(insert_data)

        result = await session.execute(stmt)
        inserted_ids = [FlashcardId(r.id) for r in result.fetchall()]

        # assign the generated IDs to the flashcards in the story collection
        for story_flashcard, new_id in zip(stories.get_all_story_flashcards(), inserted_ids):
            story_flashcard.flashcard.id = new_id

        await session.commit()
        return stories

    async def find_many(self, flashcard_ids: list[FlashcardId]) -> list[Flashcard]:
        session: AsyncSession = get_session()
        stmt = (
            select(Flashcards, FlashcardDecks)
            .join(FlashcardDecks, Flashcards.flashcard_deck_id == FlashcardDecks.id)
            .where(Flashcards.id.in_([f.value for f in flashcard_ids]))
        )
        result = await session.execute(stmt)
        return [self.map(row[0], row[1]) for row in result.fetchall()]

    async def delete(self, flashcard_id: FlashcardId) -> None:
        session: AsyncSession = get_session()
        stmt = delete(Flashcards).where(Flashcards.id == flashcard_id.value)
        await session.execute(stmt)
        await session.commit()

    async def bulk_delete(self, user_id: UserId, flashcard_ids: list[FlashcardId]) -> None:
        session: AsyncSession = get_session()
        stmt = delete(Flashcards).where(
            ((Flashcards.user_id == user_id.value) | (Flashcards.admin_id == user_id.value)),
            Flashcards.id.in_([f.value for f in flashcard_ids]),
        )
        await session.execute(stmt)
        await session.commit()

    async def update(self, flashcard: Flashcard) -> None:
        session: AsyncSession = get_session()
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = (
            update(Flashcards)
            .where(Flashcards.id == flashcard.id.value)
            .values(
                user_id=flashcard.owner.id.value if flashcard.owner.is_user() else None,
                admin_id=flashcard.owner.id.value if flashcard.owner.is_admin() else None,
                flashcard_deck_id=flashcard.deck.id.value,
                front_word=flashcard.front_word,
                front_lang=flashcard.front_lang.value,
                back_word=flashcard.back_word,
                back_lang=flashcard.back_lang.value,
                front_context=flashcard.front_context,
                back_context=flashcard.back_context,
                language_level=flashcard.language_level.value,
                emoji=flashcard.emoji.to_unicode() if flashcard.emoji else None,
                updated_at=now,
            )
        )
        await session.execute(stmt)
        await session.commit()

    async def replace_deck(
        self, actual_deck_id: FlashcardDeckId, new_deck_id: FlashcardDeckId
    ) -> None:
        session: AsyncSession = get_session()
        stmt = (
            update(Flashcards)
            .where(Flashcards.flashcard_deck_id == actual_deck_id.value)
            .values(
                flashcard_deck_id=new_deck_id.value,
                updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
        )
        await session.execute(stmt)
        await session.commit()

    def map(self, flashcard_row: Flashcards, deck_row: FlashcardDecks | None) -> Flashcard:
        deck = None
        if deck_row:
            deck = Deck(
                owner=Owner.from_user(UserId(value=deck_row.user_id))
                if deck_row.user_id
                else Owner.from_admin(UserId(value=deck_row.admin_id)),
                tag=deck_row.tag,
                name=deck_row.name,
                default_language_level=LanguageLevel(deck_row.default_language_level),
            )
            deck.id = FlashcardDeckId(deck_row.id)

        return Flashcard(
            id=FlashcardId(flashcard_row.id),
            front_word=flashcard_row.front_word,
            front_lang=Language(flashcard_row.front_lang),
            back_word=flashcard_row.back_word,
            back_lang=Language(flashcard_row.back_lang),
            front_context=flashcard_row.front_context,
            back_context=flashcard_row.back_context,
            owner=Owner.from_user(UserId(value=flashcard_row.user_id))
            if flashcard_row.user_id
            else Owner.from_admin(UserId(value=flashcard_row.admin_id)),
            deck=deck,
            level=LanguageLevel(flashcard_row.language_level),
            emoji=Emoji.from_unicode(flashcard_row.emoji) if flashcard_row.emoji else None,
        )
