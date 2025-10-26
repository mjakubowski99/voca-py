from pydantic import BaseModel
from src.flashcard.domain.models.deck import Deck


class ResolvedDeck(BaseModel):
    is_existing_deck: bool
    deck: Deck

    class Config:
        # allow attribute access like PHP getters
        allow_mutation = False

    # Optional: mimic PHP-style getters if needed
    def is_existing_deck_func(self) -> bool:
        return self.is_existing_deck

    def get_deck(self) -> Deck:
        return self.deck
