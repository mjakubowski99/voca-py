from src.flashcard.application.repository.contracts import IFlashcardDeckRepository
from src.flashcard.domain.models.deck import Deck
from src.flashcard.application.dto.resolved_deck import ResolvedDeck
from src.flashcard.domain.models.owner import Owner
from src.shared.enum import Language, LanguageLevel
from src.shared.value_objects.user_id import UserId


class DeckResolver:
    def __init__(self, repository: IFlashcardDeckRepository):
        self.repository = repository

    async def resolve_by_name(
        self,
        user_id: UserId,
        front_lang: Language,
        back_lang: Language,
        name: str,
        level: LanguageLevel,
    ) -> ResolvedDeck:
        existing_deck = await self.repository.search_by_name(user_id, name, front_lang, back_lang)

        if existing_deck:
            return ResolvedDeck(is_existing_deck=True, deck=existing_deck)

        deck = Deck(
            owner=Owner.from_user(user_id), tag=name, name=name, default_language_level=level
        )
        deck_id = await self.repository.create(deck)
        deck.id = deck_id

        return ResolvedDeck(is_existing_deck=False, deck=deck)

    async def resolve_by_id(self, deck_id: str) -> ResolvedDeck:
        deck = await self.repository.find_by_id(deck_id)
        return ResolvedDeck(existing_deck=True, deck=deck)
