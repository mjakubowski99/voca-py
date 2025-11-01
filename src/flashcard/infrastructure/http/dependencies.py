from typing import Optional
from fastapi import Query
from src.shared.enum import LanguageLevel
from src.flashcard.infrastructure.http.request import (
    GetAdminDecksRequest,
    GetUserDecksRequest,
)


def get_user_decks_query(
    search: Optional[str] = Query(None, description="Optional search term"),
    page: Optional[int] = Query(1, ge=1, description="Page number"),
    per_page: Optional[int] = Query(15, ge=1, le=100, description="Number per page"),
) -> GetUserDecksRequest:
    """Converts query params into a Pydantic request model"""
    return GetUserDecksRequest(search=search, page=page, per_page=per_page)


def get_admin_decks_query(
    search: Optional[str] = Query(None, description="Optional search term"),
    language_level: Optional[LanguageLevel] = Query(None, ge=1, description="LanguageLevel"),
    page: Optional[int] = Query(1, ge=1, description="Page number"),
    per_page: Optional[int] = Query(15, ge=1, le=100, description="Number per page"),
) -> GetAdminDecksRequest:
    """Converts query params into a Pydantic request model"""
    return GetAdminDecksRequest(
        search=search, language_level=language_level, page=page, per_page=per_page
    )
