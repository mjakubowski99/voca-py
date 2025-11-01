from abc import ABC, abstractmethod
import random


class PostgresSortCriteria(ABC):
    @abstractmethod
    def apply(self) -> str:
        pass


class EverRatedNotVeryGoodFlashcardsFirst(PostgresSortCriteria):
    VERY_GOOD_VALUE = 4  # You can replace this with your Rating enum value

    def apply(self) -> str:
        return f"COALESCE(sm_two_flashcards.min_rating,0) < {self.VERY_GOOD_VALUE} DESC"


class HardFlashcardsFirst(PostgresSortCriteria):
    def apply(self) -> str:
        return "COALESCE(sm_two_flashcards.repetition_interval, 1.0) ASC"


class LowestRepetitionIntervalFlashcardFirst(PostgresSortCriteria):
    def apply(self) -> str:
        return "COALESCE(sm_two_flashcards.repetition_interval, 1.0) ASC"


class NotHardFlashcardsFirst(PostgresSortCriteria):
    def apply(self) -> str:
        return "CASE WHEN COALESCE(sm_two_flashcards.repetition_interval, 1.0) > 1.0 THEN 1 ELSE 0 END ASC"


class NotRatedFlashcardsFirst(PostgresSortCriteria):
    def apply(self) -> str:
        return """
            CASE 
                WHEN sm_two_flashcards.repetition_interval IS NULL THEN 1
                ELSE 0
            END DESC
        """


class OlderThanFifteenSecondsAgo(PostgresSortCriteria):
    def apply(self) -> str:
        return """
            CASE 
                WHEN sm_two_flashcards.updated_at < NOW() - INTERVAL '15 seconds' THEN 0
                ELSE 1 
            END ASC
        """


class OlderThanFiveMinutesAgo(PostgresSortCriteria):
    def apply(self) -> str:
        return """
            CASE 
                WHEN sm_two_flashcards.updated_at < NOW() - INTERVAL '5 minutes' THEN 0
                ELSE 1 
            END ASC
        """


class OldestUpdateFlashcardsFirst(PostgresSortCriteria):
    def apply(self) -> str:
        return "sm_two_flashcards.updated_at ASC NULLS FIRST"


class PlannedFlashcardsForCurrentDateFirst(PostgresSortCriteria):
    def apply(self) -> str:
        return """
            CASE 
                WHEN sm_two_flashcards.updated_at IS NOT NULL AND sm_two_flashcards.repetition_interval IS NOT NULL 
                     AND DATE(sm_two_flashcards.updated_at) + CAST(sm_two_flashcards.repetition_interval AS INTEGER) = CURRENT_DATE
                THEN 2
                WHEN sm_two_flashcards.updated_at IS NOT NULL AND sm_two_flashcards.repetition_interval IS NOT NULL 
                     AND DATE(sm_two_flashcards.updated_at) + CAST(sm_two_flashcards.repetition_interval AS INTEGER) < CURRENT_DATE
                THEN 1
                ELSE 0
            END DESC
        """


class RandomizeLatestFlashcardOrder(PostgresSortCriteria):
    def apply(self) -> str:
        random_value = round(random.random(), 2)
        return f"""
            CASE 
                WHEN sm_two_flashcards.repetition_interval IS NOT NULL AND {random_value} < 0.7 THEN 1
                ELSE 0
            END DESC
        """
