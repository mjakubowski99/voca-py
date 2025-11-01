from src.flashcard.application.repository.contracts import FlashcardSortCriteria
from src.flashcard.infrastructure.repository.sm_two.criteria import (
    PostgresSortCriteria,
    EverRatedNotVeryGoodFlashcardsFirst,
    HardFlashcardsFirst,
    LowestRepetitionIntervalFlashcardFirst,
    NotHardFlashcardsFirst,
    NotRatedFlashcardsFirst,
    OlderThanFifteenSecondsAgo,
    OlderThanFiveMinutesAgo,
    OldestUpdateFlashcardsFirst,
    PlannedFlashcardsForCurrentDateFirst,
    RandomizeLatestFlashcardOrder,
)

from typing import Type


class FlashcardSortCriteriaFactory:
    _mapping: dict[FlashcardSortCriteria, Type[PostgresSortCriteria]] = {
        FlashcardSortCriteria.NOT_RATED_FLASHCARDS_FIRST: NotRatedFlashcardsFirst,
        FlashcardSortCriteria.LOWEST_REPETITION_INTERVAL_FIRST: LowestRepetitionIntervalFlashcardFirst,
        FlashcardSortCriteria.PLANNED_FLASHCARDS_FOR_CURRENT_DATE_FIRST: PlannedFlashcardsForCurrentDateFirst,
        FlashcardSortCriteria.RANDOMIZE_LATEST_FLASHCARDS_ORDER: RandomizeLatestFlashcardOrder,
        FlashcardSortCriteria.OLDEST_UPDATE_FLASHCARDS_FIRST: OldestUpdateFlashcardsFirst,
        FlashcardSortCriteria.NOT_HARD_FLASHCARDS_FIRST: NotHardFlashcardsFirst,
        FlashcardSortCriteria.HARD_FLASHCARDS_FIRST: HardFlashcardsFirst,
        FlashcardSortCriteria.OLDER_THAN_FIVE_MINUTES_AGO_FIRST: OlderThanFiveMinutesAgo,
        FlashcardSortCriteria.OLDER_THAN_FIFTEEN_SECONDS_AGO: OlderThanFifteenSecondsAgo,
        FlashcardSortCriteria.EVER_NOT_VERY_GOOD_FIRST: EverRatedNotVeryGoodFlashcardsFirst,
    }

    @staticmethod
    def make(criteria_type: FlashcardSortCriteria) -> PostgresSortCriteria:
        cls = FlashcardSortCriteriaFactory._mapping.get(criteria_type)
        if cls is None:
            raise ValueError(f"Unsupported FlashcardSortCriteria: {criteria_type}")
        return cls()
