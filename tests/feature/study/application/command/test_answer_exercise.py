import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from core.container import container
from core.models import ExerciseEntries, SmTwoFlashcards
from src.flashcard.domain.models.owner import Owner
from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.application.command.answer_exercise import AnswerExercise
from src.study.domain.enum import ExerciseStatus, Rating
from src.study.domain.value_objects import ExerciseEntryId, ExerciseId
from tests.factory import (
    FlashcardDeckFactory,
    FlashcardFactory,
    UnscrambleWordExerciseFactory,
    WordMatchExerciseFactory,
    UserFactory,
)


def get_handler() -> AnswerExercise:
    return container.resolve(AnswerExercise)


@pytest.mark.asyncio
async def test_handle_unscramble_should_assess_answer_and_update_exercise(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
    assert_db_has,
):
    # Arrange
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)

    exercise = await unscramble_word_exercise_factory.create(
        user_id=user.get_id().get_value(),
        word="banana",
        scrambled_word="anabna",
        context_sentence="I ate a banana today.",
        word_translation="banan",
        context_sentence_translation="Zjadłem dziś banana.",
        emoji="🍌",
        status=ExerciseStatus.NEW,
        flashcard_id=FlashcardId(value=flashcard.id),
    )

    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.exercise_id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    # Act
    await handler.handle_unscramble(
        user=user, entry_id=entry_id, unscrambled_word="banan", hints_count=0
    )

    # Assert
    await assert_db_has(
        ExerciseEntries,
        {
            "id": entry_id.get_value(),
            "last_answer": "banan",
            "last_answer_correct": True,
            "score": 100.0,
        },
    )


@pytest.mark.asyncio
async def test_handle_unscramble_should_save_rating_when_exercise_is_completed(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
    assert_db_has,
):
    # Arrange
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)

    exercise = await unscramble_word_exercise_factory.create(
        user_id=user.get_id().get_value(),
        word="banana",
        scrambled_word="anabna",
        context_sentence="I ate a banana today.",
        word_translation="banan",
        context_sentence_translation="Zjadłem dziś banana.",
        emoji="🍌",
        status=ExerciseStatus.NEW,
        flashcard_id=FlashcardId(value=flashcard.id),
    )

    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.exercise_id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    await handler.handle_unscramble(
        user=user, entry_id=entry_id, unscrambled_word="banan", hints_count=0
    )

    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "user_id": user.get_id().get_value(),
            "last_rating": Rating.VERY_GOOD.value,
        },
    )


@pytest.mark.asyncio
async def test_handle_unscramble_with_hints_should_penalize_score(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
    assert_db_has,
):
    # Arrange
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)

    exercise = await unscramble_word_exercise_factory.create(
        user_id=user.get_id().get_value(),
        word="banana",
        scrambled_word="anabna",
        context_sentence="I ate a banana today.",
        word_translation="banan",
        context_sentence_translation="Zjadłem dziś banana.",
        emoji="🍌",
        status=ExerciseStatus.NEW,
        flashcard_id=FlashcardId(value=flashcard.id),
    )

    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.exercise_id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    # Act - answer correctly but with hints (hints_count = 2, word length = 5, so penalty = 2/5 * 100 = 40%)
    await handler.handle_unscramble(
        user=user, entry_id=entry_id, unscrambled_word="banan", hints_count=2
    )

    # Assert - score should be penalized (100 - 40 = 60, which maps to GOOD rating)
    await assert_db_has(
        ExerciseEntries,
        {
            "id": entry_id.get_value(),
            "last_answer": "banan",
            "last_answer_correct": True,
            "answers_count": 1,
        },
    )

    # Check that the score is less than 100 due to hints penalty
    result = await session.execute(
        select(ExerciseEntries).where(ExerciseEntries.id == entry_id.get_value())
    )
    entry = result.scalars().first()
    assert entry.score < 100.0, "Score should be penalized for using hints"
    assert entry.score > 0.0, "Score should still be positive"


@pytest.mark.asyncio
async def test_handle_unscramble_with_incorrect_answer_should_not_complete_exercise(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
    assert_db_has,
):
    # Arrange
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)

    exercise = await unscramble_word_exercise_factory.create(
        user_id=user.get_id().get_value(),
        word="banana",
        scrambled_word="anabna",
        context_sentence="I ate a banana today.",
        word_translation="banan",
        context_sentence_translation="Zjadłem dziś banana.",
        emoji="🍌",
        status=ExerciseStatus.NEW,
        flashcard_id=FlashcardId(value=flashcard.id),
    )

    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.exercise_id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    # Act - answer incorrectly
    await handler.handle_unscramble(
        user=user, entry_id=entry_id, unscrambled_word="wrong", hints_count=0
    )

    # Assert - exercise should be in progress, not completed
    await assert_db_has(
        ExerciseEntries,
        {
            "id": entry_id.get_value(),
            "last_answer": "wrong",
            "last_answer_correct": False,
            "answers_count": 1,
        },
    )

    # Verify that rating was NOT saved because exercise is not completed
    result = await session.execute(
        select(SmTwoFlashcards).where(
            SmTwoFlashcards.flashcard_id == flashcard.id,
            SmTwoFlashcards.user_id == user.get_id().get_value(),
        )
    )
    sm_two = result.scalars().first()
    assert sm_two is None, "Rating should not be saved when exercise is not completed"


@pytest.mark.asyncio
async def test_handle_word_match_should_assess_answer_and_update_exercise(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    word_match_exercise_factory: WordMatchExerciseFactory,
    assert_db_has,
):
    # Arrange
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)

    exercise = await word_match_exercise_factory.create(
        user_id=user.get_id().get_value(),
        word="dog",
        word_translation="perro",
        sentence="The dog is barking.",
        flashcard_id=FlashcardId(value=flashcard.id),
        options=["dog", "cat", "bird"],
        status=ExerciseStatus.NEW,
    )

    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    # Act
    await handler.handle_word_match(
        user=user,
        exercise_id=ExerciseId(value=exercise.id),
        exercise_entry_id=entry_id,
        answer="dog",
    )

    # Assert
    await assert_db_has(
        ExerciseEntries,
        {
            "id": entry_id.get_value(),
            "last_answer": "dog",
            "last_answer_correct": True,
            "score": 100.0,
        },
    )


@pytest.mark.asyncio
async def test_handle_word_match_should_save_rating_when_exercise_is_completed(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    word_match_exercise_factory: WordMatchExerciseFactory,
    assert_db_has,
):
    # Arrange
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)

    exercise = await word_match_exercise_factory.create(
        user_id=user.get_id().get_value(),
        word="dog",
        word_translation="perro",
        sentence="The dog is barking.",
        flashcard_id=FlashcardId(value=flashcard.id),
        options=["dog", "cat", "bird"],
        status=ExerciseStatus.NEW,
    )

    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    # Act - answer correctly to complete the exercise
    await handler.handle_word_match(
        user=user,
        exercise_id=ExerciseId(value=exercise.id),
        exercise_entry_id=entry_id,
        answer="dog",
    )

    # Assert - check that rating was saved
    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "user_id": user.get_id().get_value(),
            "last_rating": Rating.VERY_GOOD.value,
        },
    )


@pytest.mark.asyncio
async def test_handle_word_match_with_incorrect_answer_should_not_complete_exercise(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    word_match_exercise_factory: WordMatchExerciseFactory,
    assert_db_has,
):
    # Arrange
    handler = get_handler()
    user = await user_factory.create_auth_user()

    owner = Owner.from_auth_user(user=user)
    deck = await deck_factory.create(owner=owner)
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)

    exercise = await word_match_exercise_factory.create(
        user_id=user.get_id().get_value(),
        word="dog",
        word_translation="perro",
        sentence="The dog is barking.",
        flashcard_id=FlashcardId(value=flashcard.id),
        options=["dog", "cat", "bird"],
        status=ExerciseStatus.NEW,
    )

    entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )
    entry_id = ExerciseEntryId(value=entry_id)

    # Act - answer incorrectly
    await handler.handle_word_match(
        user=user,
        exercise_id=ExerciseId(value=exercise.id),
        exercise_entry_id=entry_id,
        answer="cat",
    )

    # Assert - exercise should be in progress, not completed
    await assert_db_has(
        ExerciseEntries,
        {
            "id": entry_id.get_value(),
            "last_answer": "cat",
            "last_answer_correct": False,
            "answers_count": 1,
        },
    )

    # Verify that rating was NOT saved because exercise is not completed
    result = await session.execute(
        select(SmTwoFlashcards).where(
            SmTwoFlashcards.flashcard_id == flashcard.id,
            SmTwoFlashcards.user_id == user.get_id().get_value(),
        )
    )
    sm_two = result.scalars().first()
    assert sm_two is None, "Rating should not be saved when exercise is not completed"
