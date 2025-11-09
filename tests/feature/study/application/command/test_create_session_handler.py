import pytest

from src.flashcard.domain.enum import FlashcardOwnerType
from src.flashcard.domain.models.owner import Owner
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from src.flashcard.domain.value_objects import OwnerId
from src.shared.value_objects.user_id import UserId
from src.study.application.command.create_session import CreateSession, CreateSessionHandler
from core.container import container
from src.study.domain.enum import SessionType
from tests.factory import FlashcardDeckFactory, UserFactory


def get_handler() -> CreateSessionHandler:
    return container.resolve(CreateSessionHandler)


@pytest.mark.asyncio
async def test_create_and_find_unscramble_word_exercise(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
):
    user = await user_factory.create()
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(owner)
    session_handler = get_handler()

    command = CreateSession(
        user_id=UserId(value=user.id),
        session_type=SessionType.FLASHCARD,
        deck_id=FlashcardDeckId(value=deck.id),
        limit=10,
        device="Device",
    )

    session = await session_handler.handle(command)

    assert session.id != 0
    assert session.user_id.value == user.id
    assert session.deck_id.value == deck.id
    assert session.type == SessionType.FLASHCARD
    assert session.limit == 10
    assert session.device == "Device"
    assert session.new_steps == []
