from fastapi import APIRouter, Body, Depends
from core.auth import get_current_user
from core.generics import ResponseWrapper
from src.flashcard.application.command.generate_flashcards import GenerateFlashcardsHandler
from src.flashcard.application.query.get_deck_details import GetDeckDetails
from src.flashcard.application.query.get_decks_list import GetAdminDecks, GetUserDecks
from src.flashcard.infrastructure.http.dependencies import (
    get_admin_decks_query,
    get_user_decks_query,
)
from src.flashcard.infrastructure.http.mappers import (
    admin_flashcard_deck_resource_mapper,
    generate_flashcards_result_resource_mapper,
    user_flashcard_deck_resource_mapper,
)
from src.flashcard.infrastructure.http.response import (
    DeckDetailsResponse,
    FlashcardDecksResource,
)
from src.shared.user.iuser import IUser
from core.container import resolve
from src.flashcard.infrastructure.http.request import (
    GenerateFlashcards,
    GetAdminDecksRequest,
    GetUserDecksRequest,
)

router = APIRouter(tags=["Flashcard"])


@router.get("/api/v2/flashcards/decks/by-user")
async def get_user_decks(
    request: GetUserDecksRequest = Depends(get_user_decks_query),
    user: IUser = Depends(get_current_user),
    get_decks: GetUserDecks = Depends(resolve(GetUserDecks)),
) -> ResponseWrapper[FlashcardDecksResource]:
    decks = await get_decks.get(user, request.search, request.page, request.per_page)

    return user_flashcard_deck_resource_mapper(request, decks)


@router.get("/api/v2/flashcards/decks/by-admin", tags=["Flashcard"])
async def get_admin_decks(
    request: GetAdminDecksRequest = Depends(get_admin_decks_query),
    user: IUser = Depends(get_current_user),
    get_decks: GetAdminDecks = Depends(resolve(GetAdminDecks)),
) -> ResponseWrapper[FlashcardDecksResource]:
    decks = await get_decks.get(
        user, request.search, request.language_level, request.page, request.per_page
    )

    return admin_flashcard_deck_resource_mapper(request, decks)


@router.post("/api/v2/flashcards/decks/generate-flashcards", tags=["Flashcard"])
async def generate_flashcards(
    user: IUser = Depends(get_current_user),
    request: GenerateFlashcards = Body(...),
    generate_flashcards: GenerateFlashcardsHandler = Depends(resolve(GenerateFlashcardsHandler)),
    get_deck: GetDeckDetails = Depends(resolve(GetDeckDetails)),
) -> ResponseWrapper[DeckDetailsResponse]:
    result = await generate_flashcards.handle(
        request.to_command(user.get_id(), user.get_user_language(), user.get_learning_language()),
        15,
        15,
    )

    deck = await get_deck.get(user.get_id(), result.deck_id, request.page, request.per_page)

    return generate_flashcards_result_resource_mapper(deck)
