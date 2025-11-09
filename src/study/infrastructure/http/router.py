from core.generics import ResponseWrapper
from src.flashcard.domain.value_objects import SessionId
from src.study.application.command.create_session import CreateSession, CreateSessionHandler
from src.study.application.query.get_session import GetSession
from src.study.application.command.add_next_learning_step_handler import AddNextLearningStepHandler
from src.study.application.command.rate_flashcard import RateFlashcard

from fastapi import Body, Depends, Path
from core.auth import get_current_user
from core.container import container
from src.shared.user.iuser import IUser
from src.study.domain.value_objects import LearningSessionId, LearningSessionStepId
from src.study.infrastructure.http.request import CreateSessionRequest, RateFlashcardRequest
from src.study.infrastructure.http.mapper import learning_session_response_mapper
from src.study.infrastructure.http.response import LearningSessionResponse
from fastapi import APIRouter
from src.shared.value_objects.flashcard_deck_id import FlashcardDeckId
from fastapi import Request

router = APIRouter()


@router.post("/api/v2/flashcards/session", response_model=ResponseWrapper[LearningSessionResponse])
async def create_session(
    base_request: Request,
    user: IUser = Depends(get_current_user),
    request: CreateSessionRequest = Body(...),
    create_session: CreateSessionHandler = Depends(lambda: container.resolve(CreateSessionHandler)),
    add_step: AddNextLearningStepHandler = Depends(
        lambda: container.resolve(AddNextLearningStepHandler)
    ),
) -> ResponseWrapper[LearningSessionResponse]:
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
    "/api/v2/flashcards/session/{session_id}/rate-flashcard",
    response_model=ResponseWrapper[LearningSessionResponse],
)
async def rate_flashcard(
    session_id: int = Path(..., description="Session ID"),
    user: IUser = Depends(get_current_user),
    request: RateFlashcardRequest = Body(...),
    rate_flashcard: RateFlashcard = Depends(lambda: container.resolve(RateFlashcard)),
    add_step: AddNextLearningStepHandler = Depends(
        lambda: container.resolve(AddNextLearningStepHandler)
    ),
) -> ResponseWrapper[LearningSessionResponse]:
    for rating in request.ratings:
        await rate_flashcard.handle(user, LearningSessionStepId(session_id), rating.rating)

    session = await add_step.handle(user, LearningSessionId(session_id))

    return learning_session_response_mapper(session)


# async def get_session(get_session: GetSession, add_step: AddNextSessionStep):
#     session = await create_session.handle()

#     session = await add_step.handle()

#     return session


# async def rate_flashcard(
#     rate_flashcard: RateFlashcard, get_session: GetSession, add_step: AddNextSessionStep
# ):
#     await rate_flashcard.rate(session_id, rating)

#     session = await get_session.get()

#     session = await add_step.handle()

#     return session


# async def answer_unscramble_words_exercise():
#     pass


# async def answer_word_match_exercise():
#     pass


# async def skip_unscramble_words_exercise():
#     pass


# async def skip_word_match_exercise():
#     pass
