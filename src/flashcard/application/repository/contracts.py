from abc import ABC, abstractmethod
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.value_objects import FlashcardDeckId
from typing import List, Optional
from src.flashcard.domain.models.story import Story
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.domain.value_objects import StoryId, FlashcardId
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language
from src.flashcard.domain.models.flashcard import Flashcard


class IFlashcardDeckRepository(ABC):
    @abstractmethod
    async def create(self, deck: Deck) -> FlashcardDeckId:
        """Creates a new deck and returns its ID."""
        pass

    @abstractmethod
    async def find_by_id(self, deck_id: FlashcardDeckId) -> Deck:
        """Finds a deck by its ID."""
        pass

    @abstractmethod
    async def search_by_name(
        self, user_id: UserId, name: str, front_lang: Language, back_lang: Language
    ) -> Optional[Deck]:
        """Searches for a deck by name for a specific user and language pair."""
        pass

    @abstractmethod
    async def search_by_name_admin(
        self, name: str, front_lang: Language, back_lang: Language
    ) -> Optional[Deck]:
        """Searches for a deck by name for admins only."""
        pass

    @abstractmethod
    async def update(self, deck: Deck) -> None:
        """Updates an existing deck."""
        pass

    @abstractmethod
    async def update_last_viewed_at(self, deck_id: FlashcardDeckId, user_id: UserId) -> None:
        """Updates the last viewed timestamp for a user on this deck."""
        pass

    @abstractmethod
    async def get_by_user(
        self, user_id: UserId, front_lang: Language, back_lang: Language, page: int, per_page: int
    ) -> List[Deck]:
        """Returns a paginated list of decks for a user."""
        pass

    @abstractmethod
    async def remove(self, deck: Deck) -> None:
        """Removes a deck."""
        pass

    @abstractmethod
    async def delete_all_for_user(self, user_id: UserId) -> None:
        """Deletes all decks for a given user."""
        pass

    @abstractmethod
    async def bulk_delete(self, user_id: UserId, deck_ids: List[FlashcardDeckId]) -> None:
        """Deletes multiple decks by IDs for a given user."""
        pass


class IFlashcardDuplicateRepository(ABC):
    @abstractmethod
    async def get_already_saved_front_words(
        self, deck_id: FlashcardDeckId, front_words: list[str]
    ) -> list[str]:
        pass

    @abstractmethod
    async def get_random_front_word_initial_letters(
        self, deck_id: FlashcardDeckId, limit: int
    ) -> list[str]:
        pass


class IStoryRepository(ABC):
    @abstractmethod
    async def find_random_story_id_by_flashcard_id(
        self, flashcard_id: FlashcardId
    ) -> Optional[StoryId]:
        """
        Returns a random StoryId that contains the given flashcard.
        """

    @abstractmethod
    async def find(self, story_id: StoryId, user_id: UserId) -> Optional[Story]:
        """
        Returns a Story with its flashcards mapped for the given user.
        """

    @abstractmethod
    async def save_many(self, stories: StoryCollection) -> None:
        """
        Inserts multiple stories and their associated flashcards.
        """

    @abstractmethod
    async def bulk_delete(self, story_ids: List[StoryId]) -> None:
        """
        Deletes multiple stories by their IDs.
        """


class IFlashcardRepository(ABC):
    @abstractmethod
    async def get_by_category(self, deck_id: FlashcardDeckId) -> List[Flashcard]:
        """Return all flashcards belonging to a specific deck."""

    @abstractmethod
    async def get_random_flashcards(
        self, user_id: UserId, limit: int, exclude_ids: List[FlashcardId]
    ) -> List[Flashcard]:
        """Return random flashcards for a user, excluding certain IDs."""

    @abstractmethod
    async def get_random_flashcards_by_category(
        self, deck_id: FlashcardDeckId, limit: int, exclude_ids: List[FlashcardId]
    ) -> List[Flashcard]:
        """Return random flashcards from a specific deck, excluding certain IDs."""

    @abstractmethod
    async def create_many(self, flashcards: List[Flashcard]) -> None:
        """Insert multiple flashcards in bulk."""

    @abstractmethod
    async def create_many_from_story_flashcards(self, stories: StoryCollection) -> StoryCollection:
        """Insert all flashcards from a StoryCollection in bulk, assign IDs, and return the updated collection."""

    @abstractmethod
    async def find_many(self, flashcard_ids: List[FlashcardId]) -> List[Flashcard]:
        """Return multiple flashcards by their IDs."""

    @abstractmethod
    async def delete(self, flashcard_id: FlashcardId) -> None:
        """Delete a flashcard by ID."""

    @abstractmethod
    async def bulk_delete(self, user_id: UserId, flashcard_ids: List[FlashcardId]) -> None:
        """Delete multiple flashcards for a given user."""

    @abstractmethod
    async def update(self, flashcard: Flashcard) -> None:
        """Update an existing flashcard."""

    @abstractmethod
    async def replace_deck(
        self, actual_deck_id: FlashcardDeckId, new_deck_id: FlashcardDeckId
    ) -> None:
        """Move all flashcards from one deck to another."""
