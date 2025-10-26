from abc import ABC, abstractmethod
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language


class IUser(ABC):
    @abstractmethod
    def get_id(self) -> UserId:
        pass

    @abstractmethod
    def get_email(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_user_language(self) -> Language:
        pass

    @abstractmethod
    def get_learning_language(self) -> Language:
        pass
