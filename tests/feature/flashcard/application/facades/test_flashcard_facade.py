import pytest
from punq import Container
from src.flashcard.application.facades.flashcard_facade import FlashcardFacade
from src.shared.flashcard.contracts import IFlashcardGroup
from src.study.application.dto.picking_context import PickingContext
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.models.story import Story
from tests.factory import (
    FlashcardFactory,
    SmTwoFlashcardsFactory,
    UserFactory,
    FlashcardDeckFactory,
    StoryFactory,
)


@pytest.fixture
def facade(container: Container) -> FlashcardFacade:
    return container.resolve(FlashcardFacade)


@pytest.mark.asyncio
async def test_pick_flashcard_should_pick_flashcard(
    facade: FlashcardFacade,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    sm_two_factory: SmTwoFlashcardsFactory,
):
    user = await user_factory.create_auth_user()
    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner)
    higher_score_flashcard = await flashcard_factory.create(deck, owner)
    lower_score_flashcard = await flashcard_factory.create(deck, owner)

    await sm_two_factory.create(
        user.get_id().get_value(),
        flashcard_id=higher_score_flashcard.id,
        repetition_interval=13.0,
    )
    await sm_two_factory.create(
        user.get_id().get_value(),
        lower_score_flashcard.id,
        repetition_interval=12.0,
    )

    context = PickingContext(
        user=user,
        deck_id=FlashcardDeckId(value=deck.id),
        max_flashcards_count=10,
        current_count=0,
    )
    flashcard = await facade.pick_flashcard(context)

    assert flashcard.get_flashcard_id().get_value() == lower_score_flashcard.id


@pytest.mark.asyncio
async def test_pick_group_should_return_flashcard_group_when_no_story_found(
    facade: FlashcardFacade,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    sm_two_factory: SmTwoFlashcardsFactory,
):
    # Arrange
    user = await user_factory.create_auth_user()
    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner)

    # Create at least 3 flashcards for the group
    flashcard1 = await flashcard_factory.create(deck, owner, front_word="word1", back_word="słowo1")
    flashcard2 = await flashcard_factory.create(deck, owner, front_word="word2", back_word="słowo2")
    flashcard3 = await flashcard_factory.create(deck, owner, front_word="word3", back_word="słowo3")
    flashcard4 = await flashcard_factory.create(deck, owner, front_word="word4", back_word="słowo4")

    # Create SM-2 entries for all flashcards
    await sm_two_factory.create(
        user.get_id().get_value(), flashcard_id=flashcard1.id, repetition_interval=10.0
    )
    await sm_two_factory.create(
        user.get_id().get_value(), flashcard_id=flashcard2.id, repetition_interval=11.0
    )
    await sm_two_factory.create(
        user.get_id().get_value(), flashcard_id=flashcard3.id, repetition_interval=12.0
    )
    await sm_two_factory.create(
        user.get_id().get_value(), flashcard_id=flashcard4.id, repetition_interval=13.0
    )

    context = PickingContext(
        user=user,
        deck_id=FlashcardDeckId(value=deck.id),
        max_flashcards_count=10,
        current_count=0,
    )

    # Act
    group = await facade.pick_group(context)

    # Assert
    assert group is not None
    assert group.get_story_id() is None
    flashcards = group.get_flashcards()
    assert len(flashcards) == 3

    # Verify indices are set correctly
    for i, item in enumerate(flashcards):
        assert item.get_index() == i
        assert item.get_flashcard() is not None


@pytest.mark.asyncio
async def test_pick_group_should_return_story_when_story_found(
    facade: FlashcardFacade,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    sm_two_factory: SmTwoFlashcardsFactory,
    story_factory: StoryFactory,
):
    # Arrange
    user = await user_factory.create_auth_user()
    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner)

    # Create flashcards
    flashcard1 = await flashcard_factory.create(deck, owner, front_word="cat", back_word="kot")
    flashcard2 = await flashcard_factory.create(deck, owner, front_word="dog", back_word="pies")

    # Create SM-2 entries
    await sm_two_factory.create(
        user.get_id().get_value(), flashcard_id=flashcard1.id, repetition_interval=10.0
    )
    await sm_two_factory.create(
        user.get_id().get_value(), flashcard_id=flashcard2.id, repetition_interval=11.0
    )

    # Create story using factory
    await story_factory.create(
        owner=owner,
        deck=deck,
        flashcards=[flashcard1, flashcard2],
        sentence_overrides=["A cat sits.", "A dog runs."],
    )

    context = PickingContext(
        user=user,
        deck_id=FlashcardDeckId(value=deck.id),
        max_flashcards_count=10,
        current_count=0,
    )

    # Act
    group = await facade.pick_group(context)

    # Assert
    assert group is not None
    # The group should be a Story (which implements IFlashcardGroup)
    assert isinstance(group, IFlashcardGroup)
    assert group.get_story_id() is not None
    flashcards = group.get_flashcards()
    assert len(flashcards) == 2
