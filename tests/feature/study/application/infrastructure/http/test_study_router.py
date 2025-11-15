import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import ExerciseEntries, LearningSessionFlashcards, SmTwoFlashcards
from src.study.domain.enum import Rating, SessionType
from src.study.domain.value_objects import ExerciseEntryId
from tests.client import HttpClient
from tests.factory import (
    LearningSessionFactory,
    LearningSessionFlashcardFactory,
    UnscrambleWordExerciseFactory,
    UserFactory,
    WordMatchExerciseFactory,
)
from tests.factory import FlashcardDeckFactory, FlashcardFactory
from src.flashcard.domain.models.owner import Owner
from src.flashcard.domain.value_objects import FlashcardId, OwnerId
from src.flashcard.domain.enum import FlashcardOwnerType


@pytest.mark.asyncio
async def test_create_session_success(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    dump,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    await flashcard_factory.create(deck=deck, owner=owner)
    await flashcard_factory.create(deck=deck, owner=owner)

    client.login(user)
    response = await client.post(
        "/api/v2/flashcards/session",
        json={
            "session_type": "flashcard",
            "flashcard_deck_id": deck.id,
            "cards_per_session": 10,
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_session_when_unscramble_success(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    dump,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    await flashcard_factory.create(deck=deck, owner=owner)
    await flashcard_factory.create(deck=deck, owner=owner)

    client.login(user)
    response = await client.post(
        "/api/v2/flashcards/session",
        json={
            "session_type": SessionType.UNSCRAMBLE_WORDS,
            "flashcard_deck_id": deck.id,
            "cards_per_session": 10,
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_session_when_word_match_success(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    dump,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    await flashcard_factory.create(deck=deck, owner=owner)
    await flashcard_factory.create(deck=deck, owner=owner)

    client.login(user)
    response = await client.post(
        "/api/v2/flashcards/session",
        json={
            "session_type": SessionType.WORD_MATCH,
            "flashcard_deck_id": deck.id,
            "cards_per_session": 10,
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_flashcard_success(
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    assert_db_has,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)
    learning_session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=learning_session, flashcard=flashcard
    )
    client.login(user)
    response = await client.put(
        f"/api/v2/flashcards/session/{learning_session.id}/rate-flashcards",
        json={"ratings": [{"id": session_step.id, "rating": Rating.VERY_GOOD.value}]},
    )

    assert response.status_code == 200
    await assert_db_has(
        LearningSessionFlashcards, {"id": session_step.id, "rating": Rating.VERY_GOOD.value}
    )
    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "last_rating": Rating.VERY_GOOD.value,
            "repetition_interval": 6.0,
        },
    )


@pytest.mark.asyncio
async def test_answer_word_match_exercise_success(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    word_match_exercise_factory: WordMatchExerciseFactory,
    assert_db_has,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)

    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)
    learning_session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=learning_session, flashcard=flashcard
    )
    exercise = await word_match_exercise_factory.create(
        user_id=user.id,
        word="dog",
        word_translation="perro",
        sentence="The dog is barking.",
        flashcard_id=FlashcardId(value=flashcard.id),
        options=["dog", "cat", "bird"],
    )
    exercise_entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )

    client.login(user)
    response = await client.put(
        f"/api/v2/exercises/word-match/{exercise.id}/answer",
        json={"answers": [{"exercise_entry_id": exercise_entry_id, "answer": "perro"}]},
    )

    assert response.status_code == 200
    await assert_db_has(
        ExerciseEntries,
        {
            "id": exercise_entry_id,
            "last_answer": "perro",
            "last_answer_correct": True,
            "score": 100.0,
        },
    )
    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "last_rating": Rating.VERY_GOOD.value,
            "repetition_interval": 6.0,
        },
    )


@pytest.mark.asyncio
async def test_skip_word_match_exercise_success(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    word_match_exercise_factory: WordMatchExerciseFactory,
    assert_db_has,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)

    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)
    learning_session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=learning_session, flashcard=flashcard
    )

    exercise = await word_match_exercise_factory.create(
        user_id=user.id,
        word="dog",
        word_translation="perro",
        sentence="The dog is barking.",
        flashcard_id=FlashcardId(value=flashcard.id),
        options=["dog", "cat", "bird"],
    )
    exercise_entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )

    client.login(user)
    response = await client.put(
        f"/api/v2/exercises/word-match/{exercise.id}/skip",
    )

    assert response.status_code == 200
    await assert_db_has(
        ExerciseEntries,
        {"id": exercise_entry_id, "last_answer": None, "last_answer_correct": None, "score": 0.0},
    )
    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "last_rating": None,
            "repetition_interval": 1.0,
        },
    )


@pytest.mark.asyncio
async def test_skip_unscramble_words_exercise_success(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
    assert_db_has,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)

    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)
    learning_session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=learning_session, flashcard=flashcard
    )

    exercise = await unscramble_word_exercise_factory.create(
        user_id=user.id,
        word="dog",
        word_translation="perro",
        context_sentence="The dog is barking.",
        context_sentence_translation="El perro está ladrando.",
        flashcard_id=FlashcardId(value=flashcard.id),
    )
    exercise_entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )

    client.login(user)
    response = await client.put(
        f"/api/v2/exercises/unscramble-words/{exercise.id}/skip",
    )

    assert response.status_code == 200
    await assert_db_has(
        ExerciseEntries,
        {"id": exercise_entry_id, "last_answer": None, "last_answer_correct": None, "score": 0.0},
    )
    await assert_db_has(
        SmTwoFlashcards,
        {"flashcard_id": flashcard.id, "last_rating": None, "repetition_interval": 1.0},
    )


@pytest.mark.asyncio
async def test_answer_unscramble_words_exercise_success(
    session: AsyncSession,
    user_factory: UserFactory,
    deck_factory: FlashcardDeckFactory,
    flashcard_factory: FlashcardFactory,
    client: HttpClient,
    learning_session_factory: LearningSessionFactory,
    learning_session_flashcard_factory: LearningSessionFlashcardFactory,
    unscramble_word_exercise_factory: UnscrambleWordExerciseFactory,
    assert_db_has,
):
    user = await user_factory.create(email="test@example.com", password="secret1234")
    owner = Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)

    deck = await deck_factory.create(
        owner=Owner(id=OwnerId(value=user.id), flashcard_owner_type=FlashcardOwnerType.USER)
    )
    flashcard = await flashcard_factory.create(deck=deck, owner=owner)
    learning_session = await learning_session_factory.create(user_id=user.id, deck=deck)
    session_step = await learning_session_flashcard_factory.create(
        learning_session=learning_session, flashcard=flashcard
    )

    exercise = await unscramble_word_exercise_factory.create(
        user_id=user.id,
        word="dog",
        word_translation="perro",
        context_sentence="The dog is barking.",
        context_sentence_translation="El perro está ladrando.",
        flashcard_id=FlashcardId(value=flashcard.id),
    )
    exercise_entry_id = await session.scalar(
        select(ExerciseEntries.id).where(ExerciseEntries.exercise_id == exercise.id)
    )

    client.login(user)
    response = await client.put(
        f"/api/v2/exercises/unscramble-words/{exercise_entry_id}/answer",
        json={"answer": "perro", "hints_count": 0},
    )

    assert response.status_code == 200
    await assert_db_has(
        ExerciseEntries,
        {
            "id": exercise_entry_id,
            "last_answer": "perro",
            "last_answer_correct": True,
            "score": 100.0,
        },
    )
    await assert_db_has(
        SmTwoFlashcards,
        {
            "flashcard_id": flashcard.id,
            "last_rating": Rating.VERY_GOOD.value,
            "repetition_interval": 6.0,
        },
    )
