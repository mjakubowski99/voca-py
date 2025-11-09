import pytest
from core.container import container
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import SessionId
from src.study.application.command.add_next_learning_step_handler import AddNextLearningStepHandler
from src.study.domain.enum import SessionType
from tests.factory import (
    UserFactory,
    FlashcardDeckFactory,
    FlashcardFactory,
    LearningSessionFactory,
    LearningSessionFlashcardFactory,
    UnscrambleWordExerciseFactory,
)


def get_handler() -> AddNextLearningStepHandler:
    return container.resolve(AddNextLearningStepHandler)


@pytest.mark.asyncio
async def test_add_next_learning_step_handler(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
):
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    await flashcard_factory.create(deck=deck, owner=owner)
    session = await learning_session_factory.create(user_id=user.get_id().get_value(), deck=deck)
    session_id = SessionId(value=session.id)

    session = await handler.handle(user, session_id)

    assert len(session.new_steps) == 1
    assert session.new_steps[0].flashcard_exercise is not None


@pytest.mark.asyncio
async def test_add_next_learning_step_handler_should_add_unscramble_word_exercise(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
):
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    await flashcard_factory.create(deck=deck, owner=owner)
    session = await learning_session_factory.create(
        user_id=user.get_id().get_value(), deck=deck, type=SessionType.UNSCRAMBLE_WORDS
    )
    session_id = SessionId(value=session.id)

    session = await handler.handle(user, session_id)

    assert len(session.new_steps) == 1
    assert session.new_steps[0].unscramble_word_exercise is not None
