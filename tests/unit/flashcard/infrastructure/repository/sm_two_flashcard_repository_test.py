import pytest
from punq import Container
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.flashcard.application.repository.contracts import FlashcardSortCriteria
from src.flashcard.domain.value_objects import FlashcardDeckId, FlashcardId
from src.flashcard.infrastructure.repository.sm_two_flashcard_repository import (
    SmTwoFlashcardRepository,
)
from src.shared.enum import Language
from core.models import Flashcards, SmTwoFlashcards
from src.shared.value_objects.user_id import UserId
from tests.factory import (
    FlashcardPollItemFactory,
    OwnerFactory,
    FlashcardDeckFactory,
    FlashcardFactory,
    SmTwoFlashcardsFactory,
)


@pytest.fixture
def repository(container: Container) -> SmTwoFlashcardRepository:
    return container.resolve(SmTwoFlashcardRepository)


@pytest.mark.asyncio
async def test_get_next_flashcards(
    repository: SmTwoFlashcardRepository,
    session: AsyncSession,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
):
    owner = await owner_factory.create_user_owner()
    deck = await deck_factory.create(owner)

    # Create multiple flashcards
    flashcards = []
    for i in range(5):
        flashcards.append(
            await flashcard_factory.create(
                deck=deck,
                owner=owner,
                front_word=f"Front{i}",
                back_word=f"Back{i}",
                front_lang=Language.EN,
                back_lang=Language.PL,
            )
        )

    # Call method under test
    result = await repository.get_next_flashcards(
        user_id=UserId(value=owner.id.value),
        limit=3,
        exclude_flashcard_ids=[FlashcardId(f.id) for f in flashcards[:2]],
        sort_criteria=[
            FlashcardSortCriteria.EVER_NOT_VERY_GOOD_FIRST,
            FlashcardSortCriteria.NOT_HARD_FLASHCARDS_FIRST,
        ],
        cards_per_session=5,
        from_poll=False,
        exclude_from_poll=False,
        front=Language.EN,
        back=Language.PL,
    )

    # Assertions
    assert len(result) == 3
    returned_ids = [f.id.value for f in result]
    # The first two flashcards were excluded
    for f in flashcards[:2]:
        assert f.id not in returned_ids
    # The remaining flashcards should be in the result
    for f in flashcards[2:]:
        if f.id in returned_ids:
            assert f.front_word.startswith("Front")
            assert f.back_word.startswith("Back")

    # Verify data in DB is consistent
    stmt = select(Flashcards).where(Flashcards.flashcard_deck_id == deck.id)
    db_rows = (await session.execute(stmt)).scalars().all()
    assert len(db_rows) == 5


@pytest.mark.asyncio
async def test_get_next_flashcards_by_deck_filter_works(
    repository: SmTwoFlashcardRepository,
    session: AsyncSession,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    sm_two_factory: SmTwoFlashcardRepository,
):
    owner = await owner_factory.create_user_owner()
    deck = await deck_factory.create(owner)
    other_deck = await deck_factory.create(owner)

    expected = await flashcard_factory.create(deck=deck, owner=owner)
    await flashcard_factory.create(deck=other_deck, owner=owner)

    result = await repository.get_next_flashcards(
        user_id=UserId(value=owner.id.value),
        limit=3,
        exclude_flashcard_ids=[],
        sort_criteria=[],
        cards_per_session=5,
        from_poll=False,
        exclude_from_poll=False,
        front=Language.PL,
        back=Language.EN,
        deck_id=FlashcardDeckId(value=deck.id),
    )

    assert len(result) == 1
    assert result[0].id.get_value() == expected.id


@pytest.mark.asyncio
async def test_get_next_flashcards_from_poll_return_only_from_poll(
    repository: SmTwoFlashcardRepository,
    session: AsyncSession,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    flashcard_poll_factory: FlashcardPollItemFactory,
):
    owner = await owner_factory.create_user_owner()
    deck = await deck_factory.create(owner)

    await flashcard_factory.create(deck=deck, owner=owner)
    expected = await flashcard_factory.create(deck=deck, owner=owner)
    await flashcard_poll_factory.create(user_id=owner.id.value, flashcard_id=expected.id)

    result = await repository.get_next_flashcards(
        user_id=UserId(value=owner.id.value),
        limit=3,
        exclude_flashcard_ids=[],
        sort_criteria=[],
        cards_per_session=5,
        from_poll=True,
        exclude_from_poll=False,
        front=Language.PL,
        back=Language.EN,
        deck_id=FlashcardDeckId(value=deck.id),
    )

    assert len(result) == 1
    assert result[0].id.get_value() == expected.id


@pytest.mark.asyncio
async def test_get_next_flashcards_sort_by_sm_two_difficulty(
    repository: SmTwoFlashcardRepository,
    owner_factory: OwnerFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    sm_two_factory: SmTwoFlashcardsFactory,
):
    owner = await owner_factory.create_user_owner()
    deck = await deck_factory.create(owner)

    other = await flashcard_factory.create(deck=deck, owner=owner)
    expected = await flashcard_factory.create(deck=deck, owner=owner)

    await sm_two_factory.create(owner.id.value, other.id, repetition_interval=3.0)
    await sm_two_factory.create(owner.id.value, expected.id, repetition_interval=2.0)

    result = await repository.get_next_flashcards(
        user_id=UserId(value=owner.id.value),
        limit=3,
        exclude_flashcard_ids=[],
        sort_criteria=[FlashcardSortCriteria.HARD_FLASHCARDS_FIRST],
        cards_per_session=5,
        from_poll=False,
        exclude_from_poll=False,
        front=Language.PL,
        back=Language.EN,
    )

    assert len(result) == 2
    assert result[0].id.get_value() == expected.id
    assert result[1].id.get_value() == other.id
