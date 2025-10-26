from enum import Enum, IntEnum 

class FlashcardOwnerType(str, Enum):
    USER = "user"
    ADMIN = "admin"


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
