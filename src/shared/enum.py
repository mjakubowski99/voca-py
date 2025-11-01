from enum import Enum
from typing import Dict, List


class UserProvider(str, Enum):
    GOOGLE = "google"
    APPLE = "apple"


class Platform(str, Enum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"


class NotFoundException(Exception):
    pass


class Language(str, Enum):
    PL = "pl"
    EN = "en"
    IT = "it"
    ES = "es"
    FR = "fr"
    DE = "de"
    ZH = "zh"
    CS = "cs"

    @classmethod
    def values(cls) -> List[str]:
        """Return all language codes as strings."""
        return [lang.value for lang in cls]

    @classmethod
    def default_user_language(cls) -> "Language":
        return cls.PL

    @classmethod
    def default_learned_language(cls) -> "Language":
        return cls.PL

    def get_name(self) -> str:
        mapping = {
            self.PL: "Polish",
            self.EN: "English",
            self.IT: "Italian",
            self.ES: "Spanish",
            self.FR: "French",
            self.DE: "German",
            self.ZH: "Chinese",
            self.CS: "Czech",
        }
        try:
            return mapping[self]
        except KeyError:
            raise NotFoundException(f"Unknown language: {self.value}")


class LanguageLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    DEFAULT = B2

    @classmethod
    def default(cls) -> "LanguageLevel":
        """Return the default language level."""
        return cls(cls.DEFAULT)

    @classmethod
    def get_for_select_options(cls) -> Dict[str, str]:
        """Return dict of all levels for select options (value => value)."""
        return {level.value: level.value for level in cls}


class ExerciseType(str, Enum):
    UNSCRAMBLE_WORDS = "unscramble_words"
    WORD_MATCH = "word_match"

    _NUMBER_REPRESENTATIONS = {
        0: "unscramble_words",
        1: "word_match",
    }

    def to_number(self) -> int:
        for key, value in self._NUMBER_REPRESENTATIONS.items():
            if value == self.value:
                return key
        raise ValueError(f"Invalid exercise type: {self.value}")

    @classmethod
    def from_number(cls, number: int) -> "ExerciseType":
        if number not in cls._NUMBER_REPRESENTATIONS:
            raise ValueError(f"Invalid exercise type number: {number}")
        return cls(cls._NUMBER_REPRESENTATIONS[number])


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


class SessionStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

    @classmethod
    def active_statuses(cls) -> List[str]:
        return [cls.STARTED.value, cls.IN_PROGRESS.value]
