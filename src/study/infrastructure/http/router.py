from core.generics import ResponseWrapper
from src.flashcard.domain.value_objects import SessionId
from src.study.application.command.answer_exercise import AnswerExercise
from src.study.application.command.create_session import CreateSession, CreateSessionHandler
from src.study.application.command.skip_exercise import SkipExercise
from src.study.application.query.get_session import GetSession
from src.study.application.command.add_next_learning_step_handler import AddNextLearningStepHandler
from src.study.application.command.rate_flashcard import RateFlashcard

from fastapi import Body, Depends, Path
from core.auth import get_current_user
from src.shared.user.iuser import IUser
from src.study.domain.value_objects import (
    ExerciseEntryId,
    ExerciseId,
    LearningSessionId,
    LearningSessionStepId,
)
from src.study.infrastructure.http.request import (
    AnswerUnscrambleWordsExerciseRequest,
    AnswerWordMatchExerciseRequest,
    CreateSessionRequest,
    RateFlashcardRequest,
)
from src.study.infrastructure.http.mapper import learning_session_response_mapper
from src.study.infrastructure.http.response import LearningSessionResponse
from fastapi import APIRouter
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from fastapi import Request
from punq import Container
from core.container import get_container

router = APIRouter()


@router.post("/api/v2/flashcards/session", response_model=ResponseWrapper[LearningSessionResponse])
async def create_session(
    base_request: Request,
    user: IUser = Depends(get_current_user),
    request: CreateSessionRequest = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[LearningSessionResponse]:
    create_session: CreateSessionHandler = container.resolve(CreateSessionHandler)
    add_step: AddNextLearningStepHandler = container.resolve(AddNextLearningStepHandler)

    session = await create_session.handle(
        CreateSession(
            user_id=user.get_id(),
            session_type=request.session_type,
            deck_id=FlashcardDeckId(value=request.flashcard_deck_id)
            if request.flashcard_deck_id
            else None,
            limit=request.cards_per_session,
            device=base_request.headers.get("User-Agent") or "Unknown",
        )
    )

    session = await add_step.handle(user, session.id)

    return learning_session_response_mapper(session)


@router.put(
    "/api/v2/flashcards/session/{session_id}/rate-flashcards",
    response_model=ResponseWrapper[LearningSessionResponse],
)
async def rate_flashcard(
    session_id: int = Path(..., description="Session ID"),
    user: IUser = Depends(get_current_user),
    request: RateFlashcardRequest = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[LearningSessionResponse]:
    rate_flashcard: RateFlashcard = container.resolve(RateFlashcard)
    add_step: AddNextLearningStepHandler = container.resolve(AddNextLearningStepHandler)

    for rating in request.ratings:
        await rate_flashcard.handle(user, LearningSessionStepId(rating.id), rating.rating)

    session = await add_step.handle(user, LearningSessionId(session_id))

    return learning_session_response_mapper(session)


@router.get(
    "/api/v2/flashcards/session/{session_id}",
    response_model=ResponseWrapper[LearningSessionResponse],
)
async def get_session(
    session_id: int = Path(..., description="Session ID"),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[LearningSessionResponse]:
    add_step: AddNextLearningStepHandler = container.resolve(AddNextLearningStepHandler)

    session = await add_step.handle(user, LearningSessionId(value=session_id))

    return learning_session_response_mapper(session)


@router.put("/api/v2/exercises/word-match/{exercise_id}/answer")
async def answer_word_match_exercise(
    exercise_id: int = Path(..., description="Exercise ID"),
    user: IUser = Depends(get_current_user),
    request: AnswerWordMatchExerciseRequest = Body(...),
    container: Container = Depends(get_container),
) -> dict:
    answer_exercise: AnswerExercise = container.resolve(AnswerExercise)

    for answer in request.answers:
        await answer_exercise.handle_word_match(
            user, ExerciseEntryId(value=answer.exercise_entry_id), answer.answer
        )

    return {}


@router.put("/api/v2/exercises/unscramble-words/{exercise_entry_id}/answer")
async def answer_unscramble_words_exercise(
    exercise_entry_id: int = Path(..., description="Exercise entry ID"),
    user: IUser = Depends(get_current_user),
    request: AnswerUnscrambleWordsExerciseRequest = Body(...),
    container: Container = Depends(get_container),
) -> dict:
    answer_exercise: AnswerExercise = container.resolve(AnswerExercise)

    await answer_exercise.handle_unscramble(
        user, ExerciseEntryId(value=exercise_entry_id), request.answer, request.hints_count
    )

    return {}


@router.put("/api/v2/exercises/unscramble-words/{exercise_id}/skip")
async def skip_unscramble_words_exercise(
    exercise_id: int = Path(..., description="Exercise ID"),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> dict:
    skip_exercise: SkipExercise = container.resolve(SkipExercise)

    await skip_exercise.handle_unscramble(user, ExerciseId(value=exercise_id))

    return {}


@router.put("/api/v2/exercises/word-match/{exercise_id}/skip")
async def skip_word_match_exercise(
    exercise_id: int = Path(..., description="Exercise ID"),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> dict:
    skip_exercise: SkipExercise = container.resolve(SkipExercise)

    await skip_exercise.handle_word_match(user, ExerciseId(value=exercise_id))

    return {}
