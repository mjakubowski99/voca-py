import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select
from core.models import ExerciseEntries, UnscrambleWordExercises
from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.domain.enum import ExerciseStatus
from src.study.domain.models.exercise.unscramble_word_exercise import UnscrambleWordExercise
from src.study.infrastructure.repository.unscramble_word_exercise_repository import (
    UnscrambleWordExerciseRepository,
)
from src.study.domain.value_objects import ExerciseEntryId
from src.study.domain.value_objects import ExerciseId
from src.shared.value_objects.user_id import UserId
from src.study.domain.models.answer.unscramble_word_answer import UnscrambleWordAnswer
from src.shared.models import Emoji
from core.container import container
from tests.factory import (
    UserFactory,
    UnscrambleWordExerciseFactory,
)


def get_repo() -> UnscrambleWordExerciseRepository:
    return container.resolve(UnscrambleWordExerciseRepository)


@pytest.mark.asyncio
async def test_create_and_find_unscramble_word_exercise(
    user_factory: UserFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
):
    user = await user_factory.create()
    exercise = await unscramble_word_exercise_factory.build(
        user_id=user.id,
        word="banana",
        scrambled_word="anabna",
        context_sentence="I ate a banana today.",
        word_translation="banan",
        context_sentence_translation="Zjadłem dziś banana.",
        emoji="🍌",
        flashcard_id=FlashcardId(1),
    )
    exercise_id = ExerciseId(value=exercise.id)

    repo = get_repo()
    found = await repo.find(exercise_id)

    assert found.get_id().get_value() == exercise_id.get_value()
    assert found.get_word() == "banana"
    assert found.get_word_translation() == "banan"
    assert found.get_context_sentence() == "I ate a banana today."
    assert found.get_context_sentence_translation() == "Zjadłem dziś banana."
    assert found.get_emoji().to_unicode() == "🍌"


@pytest.mark.asyncio
async def test_find_by_entry_id_should_return_exercise(
    session: AsyncSession,
    user_factory: UserFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
):
    # Arrange
    user = await user_factory.create()
    exercise = await unscramble_word_exercise_factory.create(
        user_id=user.id,
        word="apple",
        context_sentence="She ate an apple.",
        word_translation="jabłko",
        context_sentence_translation="Zjadła jabłko.",
        emoji="🍎",
        flashcard_id=FlashcardId(1),
    )
    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )

    entry_id = ExerciseEntryId(value=entry_id)

    # Act
    repo = get_repo()
    found = await repo.find_by_entry_id(entry_id)

    # Assert
    assert found.get_word() == "apple"
    assert found.get_word_translation() == "jabłko"
    assert found.get_emoji().to_unicode() == "🍎"


@pytest.mark.asyncio
async def test_save_should_update_existing_exercise(
    session: AsyncSession,
    user_factory: UserFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
    assert_db_has,
):
    # Arrange
    user = await user_factory.create()
    row = await unscramble_word_exercise_factory.create(
        user_id=user.id,
        word="orange",
        context_sentence="I have an orange.",
        word_translation="pomarańcza",
        context_sentence_translation="Mam pomarańczę.",
        emoji="🍊",
        flashcard_id=FlashcardId(1),
    )
    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == row.exercise_id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    exercise = UnscrambleWordExercise(
        id=ExerciseId(value=row.exercise_id),
        user_id=UserId(value=user.id),
        flashcard_id=FlashcardId.no_id(),
        status=ExerciseStatus.IN_PROGRESS,
        answer_entry_id=entry_id,
        word=row.word,
        context_sentence=row.context_sentence,
        word_translation=row.word_translation,
        context_sentence_translation=row.context_sentence_translation,
        emoji=Emoji.from_unicode(row.emoji) if row.emoji else None,
        scrambled_word=row.scrambled_word,
        last_answer=UnscrambleWordAnswer(answer_entry_id=entry_id, unscrambled_word="orange"),
        last_answer_correct=False,
        score=0.93,
        answers_count=1,
    )
    exercise.get_exercise_entries()[0].updated = True

    repo = get_repo()

    await repo.save(exercise)

    # Assert
    await assert_db_has(ExerciseEntries, {"id": entry_id.get_value(), "score": 0.93})


@pytest.mark.asyncio
async def test_create_should_create_exercise(
    user_factory: UserFactory,
    assert_db_has,
):
    # Arrange
    user = await user_factory.create()

    exercise = UnscrambleWordExercise.new_exercise(
        user_id=UserId(value=user.id),
        word="New word",
        flashcard_id=FlashcardId(1),
        context_sentence="Test",
        word_translation="Word",
        context_sentence_translation="Test translation",
        emoji=Emoji(emoji="🍎"),
    )

    repo = get_repo()

    await repo.create(exercise)

    # Assert
    await assert_db_has(
        UnscrambleWordExercises,
        {
            "word": "New word",
        },
    )
