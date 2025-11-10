import pytest
from punq import Container
from src.flashcard.application.facades.flashcard_facade import FlashcardFacade
from src.study.application.dto.picking_context import PickingContext
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from tests.factory import (
    FlashcardFactory,
    SmTwoFlashcardsFactory,
    UserFactory,
    FlashcardDeckFactory,
)
from src.flashcard.domain.models.owner import Owner


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
