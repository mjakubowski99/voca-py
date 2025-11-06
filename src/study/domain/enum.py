from enum import Enum, IntEnum
from typing import List


class ExerciseStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    SKIPPED = "skipped"

    def is_done(self) -> bool:
        return self == ExerciseStatus.DONE


class ExerciseType(str, Enum):
    UNSCRAMBLE_WORDS = "unscramble_words"
    WORD_MATCH = "word_match"

    @staticmethod
    def _number_map() -> dict[int, str]:
        return {
            0: "unscramble_words",
            1: "word_match",
        }

    def to_number(self) -> int:
        for number, name in ExerciseType._number_map().items():
            if name == self.value:
                return number
        raise ValueError(f"Invalid exercise type: {self.value}")

    @classmethod
    def from_number(cls, number: int) -> "ExerciseType":
        mapping = cls._number_map()
        if number not in mapping:
            raise ValueError(f"Invalid exercise type number: {number}")
        return cls(mapping[number])


class SessionType(str, Enum):
    UNSCRAMBLE_WORDS = "unscramble_words"
    WORD_MATCH = "word_match"
    FLASHCARD = "flashcard"
    MIXED = "mixed"

    @classmethod
    def allowed_in_mixed(cls) -> list["SessionType"]:
        return [
            cls.FLASHCARD,
            cls.UNSCRAMBLE_WORDS,
            # cls.WORD_MATCH,  # uncomment if you want WORD_MATCH included
        ]


class LearningActivityType(str, Enum):
    FLASHCARDS = "flashcards"
    WORD_MATCH = "word_match"
    UNSCRAMBLE_WORDS = "unscramble_words"


class SessionStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

    @classmethod
    def active_statuses(cls) -> List[str]:
        return [cls.STARTED.value, cls.IN_PROGRESS.value]


class Rating(IntEnum):
    UNKNOWN = 0
    WEAK = 1
    GOOD = 2
    VERY_GOOD = 3

    @classmethod
    def max_rating(cls) -> int:
        return max(r.value for r in cls)

    @classmethod
    def max_leitner_level(cls) -> int:
        return cls.max_rating()

    def leitner_level(self) -> int:
        return self.value

    @classmethod
    def from_score(cls, score: float) -> "Rating":
        if score <= 0.3:
            return cls.UNKNOWN
        elif score <= 0.5:
            return cls.WEAK
        elif score <= 0.85:
            return cls.GOOD
        else:
            return cls.VERY_GOOD
