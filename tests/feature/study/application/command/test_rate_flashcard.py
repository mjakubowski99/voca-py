import pytest
from punq import Container
from core.models import LearningSessionFlashcards, SmTwoFlashcards
from src.flashcard.domain.value_objects import SessionId
from src.study.domain.value_objects import LearningSessionStepId
from tests.factory import (
    UserFactory,
    FlashcardDeckFactory,
    FlashcardFactory,
    LearningSessionFactory,
    LearningSessionFlashcardFactory,
)
from src.study.application.command.rate_flashcard import RateFlashcard
from src.flashcard.domain.models.owner import Owner
from src.study.domain.enum import Rating


@pytest.fixture
def handler(container: Container) -> RateFlashcard:
    return container.resolve(RateFlashcard)


async def test_rate_flashcard(
    handler: RateFlashcard,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    assert_db_has,
):
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)
    session = await learning_session_factory.create(user_id=user.get_id().get_value(), deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=session, flashcard=flashcard
    )
    session_id = SessionId(value=session.id)
    step_id = LearningSessionStepId(value=session_step.id)

    await handler.handle(user, session_id, Rating.WEAK)

    await assert_db_has(
        LearningSessionFlashcards, {"id": step_id.value, "rating": Rating.WEAK.value}
    )
    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "last_rating": Rating.WEAK.value,
            "user_id": user.get_id().get_value(),
            "repetition_ratio": 2.360000,
        },
    )
