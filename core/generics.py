from typing import Generic, TypeVar, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T", bound=BaseModel)  # T must be a Pydantic model


class ResponseWrapper(GenericModel, Generic[T]):
    data: List[T]  # Always a list of T
