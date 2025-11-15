from fastapi import APIRouter, Body, Depends, Path
from core.auth import get_current_user
from core.generics import ResponseWrapper
from src.flashcard.application.command.generate_flashcards import GenerateFlashcardsHandler
from src.flashcard.application.command.create_flashcard import CreateFlashcardHandler
from src.flashcard.application.command.merge_decks import MergeDecks
from src.flashcard.application.command.regenerate_flashcards import (
    RegenerateFlashcardsHandler,
)
from src.flashcard.application.command.update_flashcard import UpdateFlashcardHandler
from src.flashcard.application.command.bulk_delete_flashcards import BulkDeleteFlashcardsHandler
from src.flashcard.application.query.get_deck_details import GetDeckDetails
from src.flashcard.application.query.get_decks_list import GetAdminDecks, GetUserDecks
from src.flashcard.application.query.get_rating_stats import GetRatingStats
from src.flashcard.domain.value_objects import FlashcardDeckId
from src.flashcard.infrastructure.http.dependencies import (
    get_admin_decks_query,
    get_user_decks_query,
)
from src.flashcard.infrastructure.http.mappers import (
    admin_flashcard_deck_resource_mapper,
    create_flashcard_response_mapper,
    generate_flashcards_result_resource_mapper,
    user_flashcard_deck_resource_mapper,
)
from src.flashcard.infrastructure.http.response import (
    BulkDeleteFlashcardsResponse,
    DeckDetailsResponse,
    FlashcardDecksResource,
    FlashcardResponse,
    RatingStat,
    RatingStatsResponse,
)
from src.shared.user.iuser import IUser
from src.flashcard.infrastructure.http.request import (
    BulkDeleteFlashcardsRequest,
    CreateFlashcardRequest,
    GenerateFlashcards,
    GetAdminDecksRequest,
    GetUserDecksRequest,
    UpdateFlashcardRequest,
)
from punq import Container
from core.container import get_container
from src.study.infrastructure.http.mapper import rating_stats_response_mapper

router = APIRouter(tags=["Flashcard"])


@router.get("/api/v2/flashcards/decks/by-user")
async def get_user_decks(
    request: GetUserDecksRequest = Depends(get_user_decks_query),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[FlashcardDecksResource]:
    get_decks: GetUserDecks = container.resolve(GetUserDecks)

    decks = await get_decks.get(user, request.search, request.page, request.per_page)

    return user_flashcard_deck_resource_mapper(request, decks)


@router.get("/api/v2/flashcards/decks/by-admin", tags=["Flashcard"])
async def get_admin_decks(
    request: GetAdminDecksRequest = Depends(get_admin_decks_query),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[FlashcardDecksResource]:
    get_decks: GetAdminDecks = container.resolve(GetAdminDecks)
    decks = await get_decks.get(
        user, request.search, request.language_level, request.page, request.per_page
    )

    return admin_flashcard_deck_resource_mapper(request, decks)


@router.post("/api/v2/flashcards/decks/generate-flashcards", tags=["Flashcard"])
async def generate_flashcards(
    user: IUser = Depends(get_current_user),
    request: GenerateFlashcards = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[DeckDetailsResponse]:
    generate_flashcards: GenerateFlashcardsHandler = container.resolve(GenerateFlashcardsHandler)
    get_deck: GetDeckDetails = container.resolve(GetDeckDetails)

    result = await generate_flashcards.handle(
        request.to_command(user.get_id(), user.get_user_language(), user.get_learning_language()),
        15,
        15,
    )

    deck = await get_deck.get(user.get_id(), result.deck_id, request.page, request.per_page)

    return generate_flashcards_result_resource_mapper(deck)


@router.put("/api/v2/flashcards/decks/{flashcard_deck_id}/generate-flashcards", tags=["Flashcard"])
async def regenerate_flashcards(
    flashcard_deck_id: int = Path(..., description="Flashcard deck ID"),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[DeckDetailsResponse]:
    regenerate_flashcards: RegenerateFlashcardsHandler = container.resolve(
        RegenerateFlashcardsHandler
    )

    result = await regenerate_flashcards.handle(
        user, FlashcardDeckId(value=flashcard_deck_id), 15, 15
    )

    return generate_flashcards_result_resource_mapper(result.deck)


@router.post("/api/v2/flashcards", tags=["Flashcard"])
async def create_flashcard(
    user: IUser = Depends(get_current_user),
    request: CreateFlashcardRequest = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[FlashcardResponse]:
    create_flashcard_handler: CreateFlashcardHandler = container.resolve(CreateFlashcardHandler)

    command = request.to_command(
        user.get_id(),
        user.get_user_language(),
        user.get_learning_language(),
    )

    result = await create_flashcard_handler.handle(command)

    return create_flashcard_response_mapper(result.flashcard)


@router.put("/api/v2/flashcards/{flashcard_id}", tags=["Flashcard"])
async def update_flashcard(
    flashcard_id: int = Path(..., description="Flashcard ID"),
    user: IUser = Depends(get_current_user),
    request: UpdateFlashcardRequest = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[FlashcardResponse]:
    update_flashcard_handler: UpdateFlashcardHandler = container.resolve(UpdateFlashcardHandler)

    command = request.to_command(
        user.get_id(),
        flashcard_id,
        user.get_user_language(),
        user.get_learning_language(),
    )

    result = await update_flashcard_handler.handle(command)

    return create_flashcard_response_mapper(result.flashcard)


@router.delete("/api/v2/flashcards/bulk-delete", tags=["Flashcard"])
async def bulk_delete_flashcards(
    user: IUser = Depends(get_current_user),
    request: BulkDeleteFlashcardsRequest = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[BulkDeleteFlashcardsResponse]:
    bulk_delete_handler: BulkDeleteFlashcardsHandler = container.resolve(
        BulkDeleteFlashcardsHandler
    )

    command = request.to_command(user.get_id())

    result = await bulk_delete_handler.handle(command)

    return ResponseWrapper[BulkDeleteFlashcardsResponse](
        data=[BulkDeleteFlashcardsResponse(deleted_count=result.deleted_count)]
    )


@router.post("/api/v2/flashcards/decks/{from_deck_id}/merge/{to_deck_id}", tags=["Flashcard"])
async def merge_decks(
    from_deck_id: int = Path(..., description="ID of the deck to merge from"),
    to_deck_id: int = Path(..., description="ID of the deck to merge to"),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[list]:
    merge_decks_handler: MergeDecks = container.resolve(MergeDecks)

    await merge_decks_handler.handle(
        user, FlashcardDeckId(value=from_deck_id), FlashcardDeckId(value=to_deck_id)
    )

    return ResponseWrapper[list](data=[])


@router.get("/api/v2/flashcards/decks/{flashcard_deck_id}/rating-stats", tags=["Flashcard"])
async def get_rating_stats(
    flashcard_deck_id: int = Path(..., description="Flashcard deck ID"),
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[RatingStatsResponse]:
    get_rating_stats: GetRatingStats = container.resolve(GetRatingStats)
    rating_stats = await get_rating_stats.get_for_deck(
        user, FlashcardDeckId(value=flashcard_deck_id)
    )

    return rating_stats_response_mapper(rating_stats)


@router.get("/api/v2/flashcards/by-user/rating-stats", tags=["Flashcard"])
async def get_rating_stats_by_user(
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[RatingStatsResponse]:
    get_rating_stats: GetRatingStats = container.resolve(GetRatingStats)
    rating_stats = await get_rating_stats.get_for_user(user)

    return rating_stats_response_mapper(rating_stats)


@router.get("/api/v2/flashcards/by-admin/rating-stats", tags=["Flashcard"])
async def get_rating_stats_by_admin(
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[RatingStatsResponse]:
    get_rating_stats: GetRatingStats = container.resolve(GetRatingStats)
    rating_stats = await get_rating_stats.get_for_admin(user)
    return rating_stats_response_mapper(rating_stats)
