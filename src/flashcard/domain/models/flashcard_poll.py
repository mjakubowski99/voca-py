from typing import List, Union
from pydantic import BaseModel, Field, validator
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.value_objects import FlashcardId


class FlashcardPollOverLoadedException(Exception):
    pass


class FlashcardPoll(BaseModel):
    user_id: UserId
    poll_size: int
    purge_candidates: List[FlashcardId] = Field(default_factory=list)
    flashcard_ids_to_add: List[FlashcardId] = Field(default_factory=list)
    poll_limit: int = 30
    flashcard_ids_to_purge: List[FlashcardId] = Field(default_factory=list)

    class Config:
        # Allows mutation where necessary but fields can still be validated
        arbitrary_types_allowed = True

    @validator("poll_size")
    def check_poll_size(cls, v, values):
        poll_limit = values.get("poll_limit", 30)
        if v > poll_limit:
            raise FlashcardPollOverLoadedException(poll_limit, v)
        return v

    EASY_REPETITIONS_COUNT_TO_PURGE: int = 3

    def get_easy_repetitions_count_to_purge(self) -> int:
        return self.EASY_REPETITIONS_COUNT_TO_PURGE

    def replace_with_new(self, flashcard_ids: List[FlashcardId]) -> None:
        if not self.are_flashcards_to_purge() and not self.poll_is_full():
            return

        for i, old_flashcard in enumerate(self.get_purge_candidates()):
            if i < len(flashcard_ids):
                self._replace(old_flashcard, flashcard_ids[i])

    def push(self, ids: Union[FlashcardId, List[FlashcardId]]) -> None:
        if not isinstance(ids, list):
            ids = [ids]

        for i in ids:
            if self.can_add_next():
                self.flashcard_ids_to_add.append(i)
                self.poll_size += 1

    def _replace(self, old: FlashcardId, new: FlashcardId) -> None:
        self.flashcard_ids_to_add.append(new)
        self.flashcard_ids_to_purge.append(old)

    def count_to_fill_poll(self) -> int:
        return self.get_poll_limit() - self.poll_size

    def can_add_next(self) -> bool:
        return self.poll_size + 1 <= self.get_poll_limit()

    def poll_is_full(self) -> bool:
        return not self.can_add_next()

    def are_flashcards_to_purge(self) -> bool:
        return self.get_count_to_purge() > 0

    def get_count_to_purge(self) -> int:
        return len(self.purge_candidates)

    def get_purge_candidates(self) -> List[FlashcardId]:
        return self.purge_candidates

    def get_flashcard_ids_to_purge(self) -> List[FlashcardId]:
        return self.flashcard_ids_to_purge

    def get_flashcard_ids_to_add(self) -> List[FlashcardId]:
        return self.flashcard_ids_to_add

    def get_poll_limit(self) -> int:
        return self.poll_limit
