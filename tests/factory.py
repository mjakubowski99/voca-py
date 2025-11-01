# tests/factories.py
from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import (
    FlashcardPollItems,
    SmTwoFlashcards,
    Users,
    Admins,
    FlashcardDecks,
    Flashcards,
)
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.enum import FlashcardOwnerType
from src.flashcard.domain.value_objects import OwnerId
from src.shared.util.hash import IHash
from src.shared.enum import Language, LanguageLevel


class UserFactory:
    def __init__(self, session: AsyncSession, hasher: IHash):
        self.session = session
        self.hasher = hasher

    async def create(self, email: str = "test@example.com", password: str = "secret") -> Users:
        user = Users(
            id=uuid.uuid4(),
            email=email,
            name="Test User",
            password=self.hasher.make(password),
            picture=None,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        await self.session.commit()
        return user


class AdminFactory:
    def __init__(self, session: AsyncSession, hasher: IHash):
        self.session = session
        self.hasher = hasher

    async def create(
        self, email: str = "admin@example.com", password: str = "password123"
    ) -> Admins:
        admin = Admins(
            id=uuid.uuid4(),
            email=email,
            name="Test Admin",
            password=self.hasher.make(password),
        )
        self.session.add(admin)
        await self.session.flush()
        await self.session.refresh(admin)
        await self.session.commit()
        return admin


class OwnerFactory:
    def __init__(self, user_factory: UserFactory, admin_factory: AdminFactory):
        self.user_factory = user_factory
        self.admin_factory = admin_factory

    async def create_user_owner(self) -> Owner:
        user = await self.user_factory.create()
        return Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)

    async def create_admin_owner(self) -> Owner:
        admin = await self.admin_factory.create()
        return Owner(id=OwnerId(value=admin.id), flashcard_owner_type=FlashcardOwnerType.ADMIN)


class FlashcardDeckFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        owner: Owner,
        name: str = "Default Deck",
        tag: str = "default_tag",
        default_language_level: LanguageLevel = LanguageLevel.B2,
    ) -> FlashcardDecks:
        deck = FlashcardDecks(
            name=name,
            tag=tag,
            user_id=owner.id.value if owner.is_user() else None,
            admin_id=owner.id.value if owner.is_admin() else None,
            default_language_level=default_language_level.value,
        )
        self.session.add(deck)
        await self.session.flush()
        await self.session.refresh(deck)
        await self.session.commit()
        return deck


class FlashcardFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        deck: FlashcardDecks,
        owner: Owner,
        front_word: str = "Default front",
        back_word: str = "Default back",
        front_context: str = "Default context",
        back_context: str = "Default back context",
        front_lang: Language = Language.PL,
        back_lang: Language = Language.EN,
    ) -> Flashcards:
        flashcard = Flashcards(
            flashcard_deck_id=deck.id,
            front_word=front_word,
            back_word=back_word,
            front_context=front_context,
            back_context=back_context,
            front_lang=front_lang.value,
            back_lang=back_lang.value,
            user_id=owner.id.value if owner.is_user() else None,
            admin_id=owner.id.value if owner.is_admin() else None,
        )
        self.session.add(flashcard)
        await self.session.flush()
        await self.session.refresh(flashcard)
        await self.session.commit()
        return flashcard


class FlashcardPollItemFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: uuid.UUID,
        flashcard_id: int,
        easy_ratings_count: int = 0,
        easy_ratings_count_to_purge: int = 0,
        leitner_level: int = 1,
    ) -> FlashcardPollItems:
        poll_item = FlashcardPollItems(
            user_id=user_id,
            flashcard_id=flashcard_id,
            easy_ratings_count=easy_ratings_count,
            easy_ratings_count_to_purge=easy_ratings_count_to_purge,
            leitner_level=leitner_level,
        )
        self.session.add(poll_item)
        await self.session.flush()
        await self.session.refresh(poll_item)
        await self.session.commit()
        return poll_item


class SmTwoFlashcardsFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: uuid.UUID,
        flashcard_id: int,
        repetition_ratio=1.0,
        repetition_interval=2.0,
        repetition_count: int = 0,
        min_rating: int = 0,
        repetitions_in_session: int = 0,
        last_rating: Optional[int] = None,
    ) -> SmTwoFlashcards:
        sm_two = SmTwoFlashcards(
            user_id=user_id,
            flashcard_id=flashcard_id,
            repetition_ratio=repetition_ratio,
            repetition_interval=repetition_interval,
            repetition_count=repetition_count,
            min_rating=min_rating,
            repetitions_in_session=repetitions_in_session,
            last_rating=last_rating,
        )
        self.session.add(sm_two)
        await self.session.flush()
        await self.session.refresh(sm_two)
        await self.session.commit()
        return sm_two
