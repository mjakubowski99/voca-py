import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from core.models import ExerciseEntries
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import SessionId
from src.shared.flashcard.contracts import IFlashcard
from src.shared.value_objects.flashcard_id import FlashcardId
from src.shared.value_objects.user_id import UserId
from src.study.domain.enum import ExerciseType, SessionStatus, SessionType
from src.study.domain.models.learning_session import LearningSession
from src.study.domain.models.learning_session_step import LearningSessionStep
from src.study.domain.value_objects import LearningSessionId, LearningSessionStepId
from core.container import container
from tests.factory import (
    FlashcardDeckFactory,
    FlashcardFactory,
    LearningSessionFactory,
    LearningSessionFlashcardFactory,
    UnscrambleWordExerciseFactory,
    UserFactory,
)
from src.study.infrastructure.repository.session_repository import LearningSessionRepository
from unittest.mock import Mock


def get_repo() -> LearningSessionRepository:
    return container.resolve(LearningSessionRepository)


@pytest.mark.asyncio
async def test_create_should_create_new_session(user_factory: UserFactory):
    user = await user_factory.create()

    learning_session = LearningSession(
        id=LearningSessionId.no_id(),
        user_id=UserId(value=user.id),
        status=SessionStatus.IN_PROGRESS,
        type=SessionType.FLASHCARD,
        progress=0,
        limit=15,
        deck_id=None,
        device="Name",
        new_steps=[],
    )

    repo = get_repo()
    session = await repo.create(learning_session)

    assert session.id != 0
    assert session.user_id.value == user.id


@pytest.mark.asyncio
async def test_save_steps_should_save_flashcards(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    flashcard = await flashcard_factory.create(
        deck=await deck_factory.create(owner=owner), owner=owner
    )
    flaschard_mock = Mock(spec=IFlashcard)
    flaschard_mock.get_flashcard_id.return_value = FlashcardId(value=flashcard.id)

    session = await learning_session_factory.create(user.id)

    learning_session = LearningSession(
        id=LearningSessionId(value=session.id),
        user_id=UserId(value=user.id),
        status=SessionStatus.IN_PROGRESS,
        type=SessionType.FLASHCARD,
        progress=0,
        limit=15,
        deck_id=None,
        device="Name",
        new_steps=[
            LearningSessionStep(
                id=LearningSessionStepId.no_id(),
                rating=None,
                flashcard_id=FlashcardId(value=flashcard.id),
                flashcard_exercise=flaschard_mock,
            )
        ],
    )

    repo = get_repo()
    session = await repo.save_steps(learning_session)

    assert session.id.get_value() != 0
    assert session.new_steps[0].id.get_value() != 0


@pytest.mark.asyncio
async def test_find_should_build_learning_session(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    flashcard = await flashcard_factory.create(
        deck=await deck_factory.create(owner=owner), owner=owner
    )
    session = await learning_session_factory.create(user.id)
    await learning_session_flashcard_factory.create(session, flashcard, rating=None)

    repo = get_repo()
    session = await repo.find(SessionId(value=session.id))

    assert isinstance(session, LearningSession)
    assert len(session.new_steps) == 1


@pytest.mark.asyncio
async def test_find_should_build_learning_session_with_unscramble_exercise(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
):
    user = await user_factory.create()
    owner = Owner.from_user(UserId(value=user.id))
    flashcard = await flashcard_factory.create(
        deck=await deck_factory.create(owner=owner), owner=owner
    )
    learning_session = await learning_session_factory.create(user.id)
    exercise = await unscramble_word_exercise_factory.create(
        user.id,
        "banana",
        "adssda",
        "context",
        "word_translation",
        "test",
    )
    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.exercise_id)
    )
    await learning_session_flashcard_factory.create(
        learning_session,
        flashcard,
        rating=None,
        exercise_entry_id=entry_id,
        exercise_type=ExerciseType.UNSCRAMBLE_WORDS.to_number(),
    )

    repo = get_repo()
    session = await repo.find(SessionId(value=learning_session.id))

    assert isinstance(session, LearningSession)
    assert len(session.new_steps) == 1
