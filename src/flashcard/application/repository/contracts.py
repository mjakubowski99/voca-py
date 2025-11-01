from abc import ABC, abstractmethod
from core.models import SmTwoFlashcards
from src.flashcard.application.dto.deck_details_read import DeckDetailsRead
from src.flashcard.application.dto.owner_deck_read import OwnerDeckRead
from src.flashcard.domain.models.deck import Deck
from src.flashcard.domain.models.flashcard_poll import FlashcardPoll
from src.flashcard.domain.models.leitner_level_update import LeitnerLevelUpdate
from src.flashcard.domain.value_objects import FlashcardDeckId
from typing import List, Optional
from src.flashcard.domain.models.story import Story
from src.flashcard.domain.models.story_collection import StoryCollection
from src.flashcard.domain.value_objects import StoryId, FlashcardId
from src.shared.enum import LanguageLevel
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language
from src.shared.enum import Language as LanguageEnum
from src.flashcard.domain.models.flashcard import Flashcard
from enum import Enum
from src.flashcard.domain.models.next_session_flashcards import NextSessionFlashcards
from src.flashcard.domain.value_objects import SessionId
from src.shared.enum import SessionStatus
from src.flashcard.domain.models.learning_session import LearningSession
from src.flashcard.domain.models.rateable_session_flashcards import RateableSessionFlashcards


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


class IFlashcardDeckReadRepository(ABC):
    @abstractmethod
    async def find_details(
        user_id: UserId,
        flashcard_deck_id: FlashcardDeckId,
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> DeckDetailsRead:
        pass

    @abstractmethod
    async def get_admin_decks(
        self,
        user_id: UserId,
        front_lang: LanguageEnum,
        back_lang: LanguageEnum,
        level: Optional[LanguageLevel],
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> list[OwnerDeckRead]:
        pass

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UserId,
        front_lang: LanguageEnum,
        back_lang: LanguageEnum,
        search: Optional[str],
        page: int,
        per_page: int,
    ) -> list[OwnerDeckRead]:
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


class FlashcardSortCriteria(Enum):
    NOT_RATED_FLASHCARDS_FIRST = "NOT_RATED_FLASHCARDS_FIRST"
    HARD_FLASHCARDS_FIRST = "HARD_FLASHCARDS_FIRST"
    LOWEST_REPETITION_INTERVAL_FIRST = "LOWEST_REPETITION_INTERVAL_FIRST"
    PLANNED_FLASHCARDS_FOR_CURRENT_DATE_FIRST = "PLANNED_FLASHCARDS_FOR_CURRENT_DATE_FIRST"
    OLDEST_UPDATE_FLASHCARDS_FIRST = "OLDEST_UPDATE_FLASHCARDS_FIRST"
    NOT_HARD_FLASHCARDS_FIRST = "NOT_HARD_FLASHCARDS_FIRST"
    RANDOMIZE_LATEST_FLASHCARDS_ORDER = "RANDOMIZE_LATEST_FLASHCARDS_ORDER"
    OLDER_THAN_FIVE_MINUTES_AGO_FIRST = "OLDER_THAN_FIVE_MINUTES_AGO_FIRST"
    OLDER_THAN_FIFTEEN_SECONDS_AGO = "OLDER_THAN_THIRTY_SECONDS_AGO_FIRST"
    EVER_NOT_VERY_GOOD_FIRST = "EVER_NOT_VERY_GOOD_FIRST"


class ISmTwoFlashcardRepository(ABC):
    @abstractmethod
    async def reset_repetitions_in_session(self, user_id: UserId) -> None:
        """Reset repetitions_in_session to 0 for all flashcards of a given user."""
        ...

    @abstractmethod
    async def find_many(self, user_id: UserId, flashcard_ids: List[FlashcardId]) -> SmTwoFlashcards:
        """Retrieve multiple SM-2 flashcards for a user by their flashcard IDs."""
        ...

    @abstractmethod
    async def save_many(self, sm_two_flashcards: SmTwoFlashcards) -> None:
        """Save or update multiple SM-2 flashcards in bulk."""
        ...

    @abstractmethod
    async def get_next_flashcards(
        self,
        user_id: UserId,
        limit: int,
        exclude_flashcard_ids: List[FlashcardId],
        sort_criteria: List[FlashcardSortCriteria],
        cards_per_session: int,
        from_poll: bool,
        exclude_from_poll: bool,
        front: Language,
        back: Language,
        deck_id: FlashcardDeckId,
    ) -> List[Flashcard]: ...


class ISessionRepository(ABC):
    @abstractmethod
    async def update_status_by_id(
        self, session_ids: List[SessionId], status: SessionStatus
    ) -> None:
        """Update the status of multiple sessions by their IDs."""
        pass

    @abstractmethod
    async def set_all_owner_sessions_status(self, user_id: UserId, status: SessionStatus) -> None:
        """Set the status for all sessions belonging to a specific user."""
        pass

    @abstractmethod
    async def create(self, session: LearningSession) -> SessionId:
        """Create a new session and return its SessionId."""
        pass

    @abstractmethod
    async def update(self, session: LearningSession) -> None:
        """Update an existing session."""
        pass

    @abstractmethod
    async def find(self, session_id: SessionId) -> LearningSession:
        """Find and return a session by its ID."""
        pass

    @abstractmethod
    async def delete_all_for_user(self, user_id: UserId) -> None:
        """Delete all sessions for a given user."""
        pass

    @abstractmethod
    async def has_any_session(self, user_id: UserId) -> bool:
        """Return True if the user has at least one session."""
        pass


class INextSessionFlashcardsRepository(ABC):
    @abstractmethod
    async def find(self, session_id: SessionId) -> NextSessionFlashcards:
        """Retrieve NextSessionFlashcards by session ID."""
        pass

    @abstractmethod
    async def save(self, next_session_flashcards: NextSessionFlashcards) -> None:
        """Persist NextSessionFlashcards."""
        pass


class IRateableSessionFlashcardsRepository(ABC):
    @abstractmethod
    async def find(self, session_id: SessionId) -> RateableSessionFlashcards:
        """
        Finds and returns a RateableSessionFlashcards object for the given session ID.
        Raises an exception if the session does not exist.
        """
        pass

    @abstractmethod
    async def save(self, flashcards: RateableSessionFlashcards) -> None:
        """
        Saves the RateableSessionFlashcards object to the database.
        """
        pass


class IFlashcardPollRepository(ABC):
    @abstractmethod
    async def find_by_user(self, user_id: UserId, learnt_cards_purge_limit: int) -> FlashcardPoll:
        """
        Retrieves the FlashcardPoll for a given user, potentially purging
        already learnt flashcards above a certain limit.
        """
        pass

    @abstractmethod
    async def purge_latest_flashcards(self, user_id: UserId, limit: int) -> None:
        """
        Removes the latest flashcards for a user up to a specified limit.
        """
        pass

    @abstractmethod
    async def select_next_leitner_flashcard(
        self, user_id: UserId, exclude_flashcard_ids: List[FlashcardId], limit: int
    ) -> List[FlashcardPoll]:
        """
        Selects the next flashcards for the Leitner system, excluding certain flashcards.
        """
        pass

    @abstractmethod
    async def save_leitner_level_update(self, update: LeitnerLevelUpdate) -> None:
        """
        Saves an update to a flashcard's Leitner level.
        """
        pass

    @abstractmethod
    async def save(self, poll: FlashcardPoll) -> None:
        """
        Saves or updates a FlashcardPoll.
        """
        pass

    @abstractmethod
    async def reset_leitner_level_if_max_level_exceeded(
        self, user_id: UserId, max_level: int
    ) -> None:
        """
        Resets the Leitner level of flashcards if they exceed the maximum level.
        """
        pass

    @abstractmethod
    async def delete_all_by_user_id(self, user_id: UserId) -> None:
        """
        Deletes all flashcards and related polls for a given user.
        """
        pass
