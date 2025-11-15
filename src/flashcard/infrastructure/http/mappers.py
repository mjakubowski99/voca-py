from typing import List
from core.generics import ResponseWrapper
from src.flashcard.application.dto.deck_details_read import DeckDetailsRead
from src.flashcard.application.dto.owner_deck_read import OwnerDeckRead
from src.flashcard.domain.models.flashcard import Flashcard
from src.flashcard.domain.enum import GeneralRatingType
from src.flashcard.infrastructure.http.request import GetAdminDecksRequest, GetUserDecksRequest
from src.flashcard.infrastructure.http.response import (
    DeckDetailsResponse,
    FlashcardDecksResource,
    FlashcardResponse,
    OwnerDeckItem,
)


def admin_flashcard_deck_resource_mapper(
    request: GetAdminDecksRequest, decks: List[OwnerDeckRead]
) -> ResponseWrapper[FlashcardDecksResource]:
    return ResponseWrapper[FlashcardDecksResource](
        data=FlashcardDecksResource(
            decks=[
                OwnerDeckItem(
                    id=d.id.get_value(),
                    name=d.name,
                    language_level=d.language_level,
                    flashcards_count=d.flashcards_count,
                    rating_percentage=d.rating_percentage,
                    last_learnt_at=d.last_learnt_at,
                    owner_type=d.owner_type,
                )
                for d in decks
            ],
            page=request.page,
            per_page=request.per_page,
        )
    )


def user_flashcard_deck_resource_mapper(
    request: GetUserDecksRequest, decks: List[OwnerDeckRead]
) -> ResponseWrapper[FlashcardDecksResource]:
    return ResponseWrapper[FlashcardDecksResource](
        data=FlashcardDecksResource(
            decks=[
                OwnerDeckItem(
                    id=d.id.get_value(),
                    name=d.name,
                    language_level=d.language_level,
                    flashcards_count=d.flashcards_count,
                    rating_percentage=d.rating_percentage,
                    last_learnt_at=d.last_learnt_at,
                    owner_type=d.owner_type,
                )
                for d in decks
            ],
            page=request.page,
            per_page=request.per_page,
        )
    )


def generate_flashcards_result_resource_mapper(
    deck: DeckDetailsRead,
) -> ResponseWrapper[DeckDetailsResponse]:
    return ResponseWrapper[DeckDetailsResponse](
        data=DeckDetailsResponse(
            id=deck.id.value if hasattr(deck.id, "value") else int(deck.id),
            name=deck.name,
            language_level=deck.language_level.value
            if hasattr(deck.language_level, "value")
            else deck.language_level,
            last_learnt_at=deck.last_learnt_at,
            rating_percentage=deck.rating_percentage,
            owner_type=deck.owner_type.value
            if hasattr(deck.owner_type, "value")
            else deck.owner_type,
            flashcards=[
                FlashcardResponse(
                    id=f.id.value if hasattr(f.id, "value") else int(f.id),
                    front_word=f.front_word,
                    front_lang=f.front_lang.get_enum(),
                    back_word=f.back_word,
                    back_lang=f.back_lang.get_enum(),
                    front_context=f.front_context,
                    back_context=f.back_context,
                    rating=f.general_rating.value.value
                    if hasattr(f.general_rating, "value")
                    else f.general_rating,
                    language_level=f.language_level.value
                    if hasattr(f.language_level, "value")
                    else f.language_level,
                    rating_percentage=f.rating_percentage,
                    emoji=f.emoji.emoji if f.emoji else None,
                    owner_type=f.owner_type.value
                    if hasattr(f.owner_type, "value")
                    else f.owner_type,
                )
                for f in deck.flashcards
            ],
            page=deck.page,
            per_page=deck.per_page,
            flashcards_count=deck.count,
        )
    )


def create_flashcard_response_mapper(
    flashcard: Flashcard,
) -> ResponseWrapper[FlashcardResponse]:
    """
    Maps a Flashcard domain model to a FlashcardResponse for the create endpoint.
    """
    return ResponseWrapper[FlashcardResponse](
        data=FlashcardResponse(
            id=flashcard.id.value,
            front_word=flashcard.front_word,
            front_lang=flashcard.front_lang.get_enum(),
            back_word=flashcard.back_word,
            back_lang=flashcard.back_lang.get_enum(),
            front_context=flashcard.front_context,
            back_context=flashcard.back_context,
            rating=GeneralRatingType.NEW,  # New flashcard has no rating yet
            language_level=flashcard.level,
            rating_percentage=0.0,  # New flashcard has 0% rating
            emoji=flashcard.emoji.to_unicode() if flashcard.emoji else None,
            owner_type=flashcard.get_owner_type(),
        )
    )
