from typing import List
from src.shared.enum import Language as LanguageEnum
from src.shared.enum import LanguageLevel


class Language:
    model_config = {"arbitarty_types_allowed": True}
    DEFAULT_LEVELS: List[LanguageLevel] = [
        LanguageLevel.A1,
        LanguageLevel.A2,
        LanguageLevel.B1,
        LanguageLevel.B2,
        LanguageLevel.C1,
        LanguageLevel.C2,
    ]

    LANGUAGE_LEVELS = {
        LanguageEnum.PL.value: DEFAULT_LEVELS,
        LanguageEnum.EN.value: DEFAULT_LEVELS,
        LanguageEnum.IT.value: DEFAULT_LEVELS,
        LanguageEnum.ES.value: DEFAULT_LEVELS,
        LanguageEnum.FR.value: DEFAULT_LEVELS,
        LanguageEnum.DE.value: DEFAULT_LEVELS,
        LanguageEnum.ZH.value: DEFAULT_LEVELS,
        LanguageEnum.CS.value: DEFAULT_LEVELS,
    }

    def __init__(self, value: str):
        if value not in LanguageEnum.values():
            raise ValueError(f"Invalid language: {value}")
        self._value: LanguageEnum = LanguageEnum(value)

    @classmethod
    def from_string(cls, value: str) -> "Language":
        return cls(value)

    @classmethod
    def all(cls) -> List["Language"]:
        return [cls(lang.value) for lang in LanguageEnum]

    # Static constructors for each language
    @classmethod
    def pl(cls) -> "Language":
        return cls(LanguageEnum.PL.value)

    @classmethod
    def en(cls) -> "Language":
        return cls(LanguageEnum.EN.value)

    @classmethod
    def it(cls) -> "Language":
        return cls(LanguageEnum.IT.value)

    @classmethod
    def es(cls) -> "Language":
        return cls(LanguageEnum.ES.value)

    @classmethod
    def fr(cls) -> "Language":
        return cls(LanguageEnum.FR.value)

    @classmethod
    def de(cls) -> "Language":
        return cls(LanguageEnum.DE.value)

    @classmethod
    def zh(cls) -> "Language":
        return cls(LanguageEnum.ZH.value)

    @classmethod
    def cs(cls) -> "Language":
        return cls(LanguageEnum.CS.value)

    def get_enum(self) -> LanguageEnum:
        return self._value

    def get_value(self) -> str:
        return self._value.value

    def get_available_levels(self) -> List[LanguageLevel]:
        return self.LANGUAGE_LEVELS[self._value.value]

    def __str__(self) -> str:
        return self._value.value

    def __repr__(self) -> str:
        return f"Language({self._value.value})"
