from typing import TypeVar, ClassVar
from pydantic import BaseModel, Field, ConfigDict
from abc import ABC

T = TypeVar("T", bound="IntegerId")


class IntegerId(BaseModel, ABC):
    """Abstract base class for integer ID value objects"""

    NO_ID_VALUE: ClassVar[int] = 0

    value: int = Field(ge=0)

    model_config = ConfigDict(frozen=True)  # Immutable

    def __init__(self, value: int = 0, **kwargs):
        super().__init__(value=value, **kwargs)

    @classmethod
    def no_id(cls: type[T]) -> T:
        """Create an empty/no-id instance"""
        return cls(value=cls.NO_ID_VALUE)

    def is_empty(self) -> bool:
        """Check if this is a no-id value"""
        return self.value == self.NO_ID_VALUE

    def get_no_id_value(self) -> int:
        """Get the no-id constant value"""
        return self.NO_ID_VALUE

    def get_value(self) -> int:
        """Get the ID value, raises if empty"""
        if self.value == self.NO_ID_VALUE:
            raise ValueError("Cannot retrieve no id value")
        return self.value

    def __str__(self) -> str:
        """String representation, raises if empty"""
        if self.value == self.NO_ID_VALUE:
            raise ValueError("Cannot retrieve no id value")
        return str(self.value)

    def __int__(self) -> int:
        """Integer representation"""
        return self.get_value()

    def __eq__(self, other: object) -> bool:
        """Check equality with another ID"""
        if not isinstance(other, self.__class__):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """Make it hashable for use in sets/dicts"""
        return hash((self.__class__.__name__, self.value))
