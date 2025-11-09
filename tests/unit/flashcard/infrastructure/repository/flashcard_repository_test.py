import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.story import Story
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.domain.models.story_flashcard import StoryFlashcard
from src.flashcard.domain.value_objects import FlashcardDeckId, FlashcardId
from src.shared.value_objects.story_id import StoryId
from src.flashcard.infrastructure.repository.flashcard_repository import FlashcardRepository
from src.flashcard.domain.models.flashcard import Flashcard
from src.shared.models import Emoji
from src.shared.value_objects.language import Language
from src.shared.enum import LanguageLevel
from core.models import Flashcards
from tests.factory import FlashcardDeckFactory, OwnerFactory
from core.container import container


def get_repo() -> FlashcardRepository:
    return container.resolve(FlashcardRepository)


@pytest.mark.asyncio
async def test_create_many_should_insert_flashcards(
    session: AsyncSession, owner_factory: OwnerFactory, deck_factory: FlashcardDeckFactory
):
    """
    Ensures that FlashcardRepository.create_many() correctly inserts multiple flashcards
    into the database, preserving language fields, context, and emoji.
    """
    repo = get_repo()
    user = await owner_factory.create_user_owner()
    deck = await deck_factory.create(user)

    # Build flashcards (domain objects)
    flashcards = []
    for i in range(3):
        flashcards.append(
            Flashcard(
                id=FlashcardId.no_id(),
                front_word=f"Front{i}",
                front_lang=Language.en(),
                back_word=f"Back{i}",
                back_lang=Language.pl(),
                front_context=f"Front context {i}",
                back_context=f"Back context {i}",
                owner=user,
                deck=Deck(
                    id=FlashcardDeckId(value=deck.id),
                    owner=user,
                    tag=deck.tag,
                    name=deck.name,
                    default_language_level=LanguageLevel.A1,
                ),
                level=LanguageLevel.A1,
                emoji=Emoji.from_unicode("🐍"),
            )
        )

    # Call the method under test
    await repo.create_many(flashcards)

    # Verify flashcards were inserted
    stmt = select(Flashcards).where(Flashcards.flashcard_deck_id == deck.id)
    result = await session.execute(stmt)
    rows = result.scalars().all()

    assert len(rows) == 3
    for i, row in enumerate(rows):
        assert row.front_word == f"Front{i}"
        assert row.back_word == f"Back{i}"
        assert row.front_lang == Language.en().get_value()
        assert row.back_lang == Language.pl().get_value()
        assert row.front_context == f"Front context {i}"
        assert row.back_context == f"Back context {i}"
        assert row.language_level == LanguageLevel.A1.value
        assert row.emoji == "🐍"
        # Created_at and updated_at should be recent UTC timestamps
        assert isinstance(row.created_at, datetime)
        assert row.created_at.tzinfo is None  # naive UTC datetime stored in DB


@pytest.mark.asyncio
async def test_create_many_from_story_flashcards(
    session: AsyncSession, owner_factory: OwnerFactory, deck_factory: FlashcardDeckFactory
):
    """
    Test that FlashcardRepository.create_many_from_story_flashcards inserts all flashcards
    from a StoryCollection and assigns IDs correctly.
    """
    repo = get_repo()
    user = await owner_factory.create_user_owner()
    deck = await deck_factory.create(user)

    # Build StoryCollection with 3 flashcards
    flashcards = []
    for i in range(3):
        flashcards.append(
            Flashcard(
                id=FlashcardId.no_id(),
                front_word=f"Front{i}",
                front_lang=Language.en(),
                back_word=f"Back{i}",
                back_lang=Language.pl(),
                front_context=f"Front context {i}",
                back_context=f"Back context {i}",
                owner=user,
                deck=Deck(
                    id=FlashcardDeckId(value=deck.id),
                    owner=user,
                    tag=deck.tag,
                    name=deck.name,
                    default_language_level=LanguageLevel.A1,
                ),
                level=LanguageLevel.A1,
                emoji=Emoji.from_unicode("🔥"),
            )
        )

    stories = StoryCollection(
        stories=[
            Story(
                id=StoryId.no_id(),
                flashcards=[
                    StoryFlashcard(
                        story_id=StoryId.no_id(),
                        story_index=1,
                        sentence_override=None,
                        flashcard=flashcard,
                    )
                    for flashcard in flashcards
                ],
            )
        ]
    )

    # Call method under test
    updated_stories = await repo.create_many_from_story_flashcards(stories)

    # Check returned collection
    inserted_flashcards = list(updated_stories.get_all_story_flashcards())

    # Verify flashcards in DB
    stmt = select(Flashcards).where(Flashcards.flashcard_deck_id == deck.id)
    result = await session.execute(stmt)
    rows = result.scalars().all()

    assert len(list(rows)) == 3
    assert len(list(inserted_flashcards)) == 3

    for i, row in enumerate(rows):
        assert row.front_word == f"Front{i}"
        assert row.back_word == f"Back{i}"
        assert row.front_lang == Language.en().get_value()
        assert row.back_lang == Language.pl().get_value()
        assert row.emoji == "🔥"  # stored as alias
        # verify StoryCollection flashcard ID was assigned
        assert inserted_flashcards[i].flashcard.id.value == row.id
