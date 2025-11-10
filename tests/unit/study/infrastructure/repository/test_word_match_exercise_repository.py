from punq import Container
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.container import container
from core.models import ExerciseEntries, Exercises
from src.shared.value_objects.flashcard_id import FlashcardId
from src.shared.value_objects.story_id import StoryId
from src.shared.value_objects.user_id import UserId
from src.study.domain.enum import ExerciseStatus, ExerciseType
from src.study.domain.models.answer.word_match_answer import WordMatchAnswer
from src.study.domain.models.exercise.word_match_exercise import WordMatchExercise
from src.study.domain.models.exercise_entry.exercise_entry import ExerciseEntry
from src.study.domain.models.exercise_entry.word_match_exercise_entry import WordMatchExerciseEntry
from src.study.domain.value_objects import ExerciseEntryId, ExerciseId
from src.study.infrastructure.repository.word_match_exercise_repository import (
    WordMatchExerciseRepository,
)
from tests.factory import ExerciseEntryFactory, ExerciseFactory, UserFactory


@pytest.fixture
def repository(container: Container) -> WordMatchExerciseRepository:
    return container.resolve(WordMatchExerciseRepository)


@pytest.mark.asyncio
async def test_create_word_match_exercise(
    repository: WordMatchExerciseRepository, user_factory: UserFactory, assert_db_has
):
    user = await user_factory.create_auth_user()
    entries = [
        WordMatchExerciseEntry(
            word="dog",
            word_translation="perro",
            sentence="The dog is barking.",
            id=ExerciseEntryId.no_id(),
            exercise_id=ExerciseId.no_id(),
            flashcard_id=FlashcardId(1),
            correct_answer=WordMatchAnswer(answer_entry_id=ExerciseEntryId.no_id(), word="dog"),
            last_user_answer=None,
            last_answer_correct=None,
            order=0,
            score=0.0,
            answers_count=0,
        ),
        WordMatchExerciseEntry(
            word="cat",
            word_translation="gato",
            sentence="The cat is sleeping.",
            id=ExerciseEntryId.no_id(),
            exercise_id=ExerciseId.no_id(),
            flashcard_id=FlashcardId(1),
            correct_answer=WordMatchAnswer(answer_entry_id=ExerciseEntryId.no_id(), word="cat"),
            last_user_answer=None,
            last_answer_correct=None,
            order=1,
            score=0.0,
            answers_count=0,
        ),
    ]
    word_match = WordMatchExercise(
        exercise_id=ExerciseId.no_id(),
        user_id=user.get_id(),
        status=ExerciseStatus.IN_PROGRESS,
        exercise_entries=entries,
        options=["dog", "cat", "bird"],
        story_id=None,
    )
    exercise = await repository.create(word_match)
    assert exercise.id.value != 0

    await assert_db_has(
        Exercises,
        {
            "id": exercise.id.value,
            "user_id": user.get_id().value,
            "status": ExerciseStatus.IN_PROGRESS.value,
        },
    )
    await assert_db_has(
        ExerciseEntries,
        {
            "exercise_id": exercise.id.value,
            "order": 0,
            "last_answer": None,
            "correct_answer": "dog",
        },
    )
    await assert_db_has(
        ExerciseEntries,
        {
            "exercise_id": exercise.id.value,
            "order": 1,
            "last_answer": None,
            "correct_answer": "cat",
        },
    )


@pytest.mark.asyncio
async def test_find_word_match_exercise(
    repository: WordMatchExerciseRepository,
    assert_db_has,
    user_factory: UserFactory,
    exercise_factory: ExerciseFactory,
    exercise_entry_factory: ExerciseEntryFactory,
):
    user = await user_factory.create_auth_user()

    exercise = await exercise_factory.create(
        user_id=user.get_id().value,
        exercise_type=ExerciseType.WORD_MATCH,
        status=ExerciseStatus.IN_PROGRESS,
        properties={
            "story_id": 3,
            "sentences": [
                {
                    "order": 0,
                    "flashcard_id": 1,
                    "sentence": "The fox jumps.",
                    "word": "fox",
                    "translation": "zorro",
                },
                {
                    "order": 1,
                    "flashcard_id": 2,
                    "sentence": "The dog runs.",
                    "word": "dog",
                    "translation": "perro",
                },
            ],
            "answer_options": ["fox", "dog", "cat"],
        },
    )
    (await exercise_entry_factory.create(exercise, order=0, correct_answer="fox", score=0.1),)
    (await exercise_entry_factory.create(exercise, order=1, correct_answer="dog", score=0.1),)

    found = await repository.find(ExerciseId(exercise.id))

    assert found.id.value == exercise.id
    assert found.user_id.value == exercise.user_id
    assert found.status == ExerciseStatus.IN_PROGRESS
    assert found.options == ["fox", "dog", "cat"]
    assert len(found.exercise_entries) == 2
    assert found.story_id.value == 3

    for idx, entry in enumerate[WordMatchExerciseEntry](found.exercise_entries):
        assert entry.order == idx
        assert entry.correct_answer.to_string() in ("fox", "dog")
        assert entry.word_translation in ("zorro", "perro")
        assert entry.sentence in ("The fox jumps.", "The dog runs.")
        assert entry.score == 0.1
        assert entry.answers_count == 0
        assert entry.last_user_answer is None


@pytest.mark.asyncio
async def test_save_word_match_exercise(
    repository: WordMatchExerciseRepository,
    assert_db_has,
    user_factory: UserFactory,
    exercise_factory: ExerciseFactory,
    exercise_entry_factory: ExerciseEntryFactory,
):
    user = await user_factory.create_auth_user()
    exercise = await exercise_factory.create(
        user_id=user.get_id().value,
        exercise_type=ExerciseType.WORD_MATCH,
        status=ExerciseStatus.IN_PROGRESS,
        properties={
            "story_id": None,
            "sentences": [
                {
                    "order": 0,
                    "flashcard_id": 1,
                    "sentence": "Test A.",
                    "word": "A",
                    "translation": "uno",
                },
            ],
            "answer_options": ["A", "B"],
        },
    )
    entry = await exercise_entry_factory.create(
        exercise=exercise,
        correct_answer="A",
        score=0.0,
        answers_count=0,
        last_answer=None,
        last_answer_correct=None,
        order=0,
    )

    obj = WordMatchExercise(
        story_id=None,
        exercise_id=ExerciseId(value=exercise.id),
        user_id=UserId(value=exercise.user_id),
        status=ExerciseStatus.DONE,
        exercise_entries=[
            WordMatchExerciseEntry(
                word="A",  # As per the test data
                word_translation="uno",
                sentence="Test A.",
                flashcard_id=FlashcardId(value=1),
                id=ExerciseEntryId(entry.id),
                exercise_id=ExerciseId(exercise.id),
                correct_answer=WordMatchAnswer(answer_entry_id=ExerciseEntryId(entry.id), word="A"),
                last_user_answer=WordMatchAnswer(
                    answer_entry_id=ExerciseEntryId(entry.id), word="A"
                ),
                last_answer_correct=True,
                order=0,
                score=42.0,
                answers_count=4,
                updated=True,
            )
        ],
        options=["A", "B"],
    )

    await repository.save(exercise)

    await assert_db_has(Exercises, {"id": exercise.id, "status": ExerciseStatus.DONE.value})
    await assert_db_has(
        ExerciseEntries,
        {
            "id": entry.id,
            "answers_count": 4,
            "score": 42.0,
            "last_answer": "A",
            "last_answer_correct": True,
        },
    )


@pytest.mark.asyncio
async def test_find_raises_if_not_found(repository: WordMatchExerciseRepository):
    with pytest.raises(Exception) as exc:
        await repository.find(ExerciseId(123456789))
    assert "No Word Match Exercise found for entry ID: 123456789" in str(exc.value)
