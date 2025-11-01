from typing import List, Optional
import random
from flashcard.domain.models.next_session_flashcard import Flashcard, NextSessionFlashcard
from flashcard.domain.value_objects import SessionId, FlashcardId
from src.flashcard.domain.models.session_flashcards_base import SessionFlashcardsBase
from src.shared.enum import SessionType, ExerciseType
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.models.session_flashcard_summaries import SessionFlashcardSummaries
from src.flashcard.domain.enum import Rating
from flashcard.domain.models.deck import Deck
from src.shared.value_objects.exercise_entry_id import ExerciseEntryId


class InvalidNextSessionFlashcards(Exception):
    pass


class TooManySessionFlashcardsException(Exception):
    pass


class NextSessionFlashcards(SessionFlashcardsBase):
    UNRATED_LIMIT = 5

    def __init__(
        self,
        session_id: SessionId,
        session_type: SessionType,
        user_id: UserId,
        deck: Optional[Deck],
        current_session_flashcards_count: int,
        unrated_count: int,
        max_flashcards_count: int,
    ):
        self._session_id = session_id
        self._type = session_type
        self._user_id = user_id
        self._deck = deck
        self._current_session_flashcards_count = current_session_flashcards_count
        self._unrated_count = unrated_count
        self._max_flashcards_count = max_flashcards_count
        self._next_session_flashcards: List[NextSessionFlashcard] = []
        self._additional_flashcards: List[NextSessionFlashcard] = []

        if not self.is_valid():
            raise InvalidNextSessionFlashcards(
                f"Cannot generate next session flashcards for session: {self._session_id.value}"
            )

    # Getters
    def get_session_id(self) -> SessionId:
        return self._session_id

    def get_session_type(self) -> SessionType:
        return self._type

    def get_user_id(self) -> UserId:
        return self._user_id

    def get_deck(self) -> Optional[Deck]:
        return self._deck

    def get_max_flashcards_count(self) -> int:
        return self._max_flashcards_count

    def get_current_session_flashcards_count(self) -> int:
        return self._current_session_flashcards_count

    def get_unrated_count(self) -> int:
        return self._unrated_count

    def get_next_flashcards(self) -> List[NextSessionFlashcard]:
        return self._next_session_flashcards

    def get_additional_flashcards(self) -> List[NextSessionFlashcard]:
        return self._additional_flashcards

    def has_deck(self) -> bool:
        return self._deck is not None

    # Validation
    def is_valid(self) -> bool:
        if self._unrated_count > self.UNRATED_LIMIT:
            return False
        return self._current_session_flashcards_count <= self._max_flashcards_count

    def can_add_next(self) -> bool:
        if self._unrated_count + 1 > self.UNRATED_LIMIT:
            return False
        return self._current_session_flashcards_count + 1 <= self._max_flashcards_count

    # Flashcard management
    def add_flashcards_from_summaries(self, summaries: SessionFlashcardSummaries) -> None:
        for summary in summaries.get_summaries():
            if not self.can_add_next():
                return
            if summary.is_additional:
                self.add_next_additional(summary.flashcard)
            else:
                self.add_next(summary.flashcard)

    def add_next(self, flashcard: Flashcard) -> None:
        if not self.can_add_next():
            raise TooManySessionFlashcardsException()
        self._next_session_flashcards.append(NextSessionFlashcard(flashcard.id))
        self._current_session_flashcards_count += 1
        self._unrated_count += 1

    def add_next_additional(self, flashcard: Flashcard) -> None:
        self._additional_flashcards.append(NextSessionFlashcard(flashcard.id))

    # Exercise association
    def associate_exercise_entries(self, entries: List, exercise_type: ExerciseType) -> None:
        for entry in entries:
            self.associate_exercise(
                FlashcardId(entry.flashcard_id), entry.exercise_entry_id, exercise_type
            )

    def associate_exercise(
        self,
        flashcard_id: FlashcardId,
        exercise_entry_id: ExerciseEntryId,
        exercise_type: ExerciseType,
    ) -> None:
        for flashcard in self._next_session_flashcards + self._additional_flashcards:
            if flashcard_id == flashcard.flashcard_id:
                flashcard.set_exercise(exercise_entry_id, exercise_type)
                return

    # Exercise resolution
    def is_mixed_session_type(self) -> bool:
        return self._type == SessionType.MIXED

    def resolve_exercise_by_rating(self, rating: Optional[Rating]) -> Optional[ExerciseType]:
        exercise_type = self.resolve_next_exercise_type()
        if self.is_mixed_session_type() and (rating is None or rating.value < Rating.GOOD.value):
            return None
        return exercise_type

    def resolve_next_exercise_type(self) -> Optional[ExerciseType]:
        type_ = self._type
        if type_ == SessionType.MIXED:
            type_ = random.choice(SessionType.allowed_in_mixed())
        if type_ == SessionType.UNSCRAMBLE_WORDS:
            return ExerciseType.UNSCRAMBLE_WORDS
        if type_ == SessionType.WORD_MATCH:
            return ExerciseType.WORD_MATCH
        return None
