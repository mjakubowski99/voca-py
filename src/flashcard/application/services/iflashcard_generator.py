from abc import ABC, abstractmethod
from src.flashcard.domain.flashcard_models import Owner, Deck
from src.flashcard.domain.flashcard_prompt import FlashcardPrompt
from src.flashcard.domain.models.story_collection import StoryCollection


class IFlashcardGenerator(ABC):
    @abstractmethod
    async def generate(self, owner: Owner, deck: Deck, prompt: FlashcardPrompt) -> StoryCollection:
        """
        Generate a StoryCollection of flashcards for the given owner, deck, and prompt.
        """
        pass
