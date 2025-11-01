import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models import Stories, StoryFlashcards, Flashcards
from src.flashcard.infrastructure.repository.story_repository import StoryRepository
from src.flashcard.infrastructure.repository.flashcard_repository import FlashcardRepository
from src.flashcard.domain.models.story import Story
from src.flashcard.domain.models.story_flashcard import StoryFlashcard
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.emoji import Emoji
from src.shared.value_objects.language import Language
from src.shared.enum import LanguageLevel
from src.flashcard.domain.value_objects import FlashcardDeckId, FlashcardId, StoryId
from tests.factory import FlashcardDeckFactory, OwnerFactory


@pytest.mark.asyncio
async def test_save_many_should_insert_stories_and_story_flashcards(
    session: AsyncSession, owner_factory: OwnerFactory, deck_factory: FlashcardDeckFactory
):
    # Arrange
    flashcard_repo = FlashcardRepository()
    repo = StoryRepository(flashcard_repo=flashcard_repo)

    # Fake user/deck setup
    user = await owner_factory.create_user_owner()
    deck = await deck_factory.create(user)

    # Create Flashcard domain objects
    flashcard1 = Flashcard(
        id=FlashcardId.no_id(),
        front_word="cat",
        front_lang=Language.en(),
        back_word="kot",
        back_lang=Language.pl(),
        front_context="A small cat.",
        back_context="Mały kot.",
        owner=user,
        deck=Deck(
            id=FlashcardDeckId(value=deck.id),
            owner=user,
            tag=deck.tag,
            name=deck.name,
            default_language_level=LanguageLevel.A1,
        ),
        level=LanguageLevel.A1,
        emoji=Emoji(emoji="🐱"),
    )

    flashcard2 = Flashcard(
        id=FlashcardId.no_id(),
        front_word="dog",
        front_lang=Language.en(),
        back_word="pies",
        back_lang=Language.pl(),
        front_context="A small dog.",
        back_context="Mały pies.",
        owner=user,
        deck=Deck(
            id=FlashcardDeckId(value=deck.id),
            owner=user,
            tag=deck.tag,
            name=deck.name,
            default_language_level=LanguageLevel.A1,
        ),
        level=LanguageLevel.A1,
        emoji=Emoji(emoji="🐶"),
    )

    # Create Story and StoryFlashcards
    story = Story(id=StoryId.no_id(), flashcards=[])
    story_flashcard_1 = StoryFlashcard(
        story_id=StoryId(value=0),
        story_index=1,
        flashcard=flashcard1,
        sentence_override="A cat sits.",
    )
    story_flashcard_2 = StoryFlashcard(
        story_id=StoryId.no_id(),
        story_index=2,
        flashcard=flashcard2,
        sentence_override="A dog runs.",
    )
    story.flashcards = [story_flashcard_1, story_flashcard_2]

    # Wrap in collection
    stories = StoryCollection(stories=[story])

    # Act
    await repo.save_many(stories)

    # Assert
    # Verify Stories inserted
    inserted_stories = (await session.execute(select(Stories))).scalars().all()
    assert len(inserted_stories) == 1

    # Verify Flashcards inserted
    inserted_flashcards = (await session.execute(select(Flashcards))).scalars().all()
    assert len(inserted_flashcards) == 2

    # Verify StoryFlashcards inserted
    inserted_story_flashcards = (await session.execute(select(StoryFlashcards))).scalars().all()
    assert len(inserted_story_flashcards) == 2

    # Check story_flashcard link integrity
    assert inserted_story_flashcards[0].story_id == inserted_stories[0].id
    assert inserted_story_flashcards[0].flashcard_id == inserted_flashcards[0].id

    # Check emoji persisted properly
    assert inserted_flashcards[0].emoji in ("🐱", "\U0001f431")
    assert inserted_flashcards[1].emoji in ("🐶", "\U0001f436")
