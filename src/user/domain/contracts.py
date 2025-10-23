from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
from src.shared.enum import Platform, UserProvider
from abc import ABC, abstractmethod
from src.shared.value_objects.user_id import UserId
from src.shared.value_objects.language import Language


class IOAuthUser(ABC):
    
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_user_provider(self) -> UserProvider:
        pass

    @abstractmethod
    def get_name(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_email(self) -> str:
        pass

    @abstractmethod
    def get_nickname(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_avatar(self) -> Optional[str]:
        pass

class IOAuthLogin(ABC):

    @abstractmethod
    async def login(self, provider: UserProvider, token: str, platform: Platform) -> IOAuthUser:
        pass


class IUser(ABC):
    
    @abstractmethod
    def get_id(self) -> UserId:
        """Return the unique user ID."""
        pass

    @abstractmethod
    def get_password(self) -> str:
        """Return the user's password hash."""
        pass

    @abstractmethod
    def get_email(self) -> str:
        """Return the user's email."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the user's full name."""
        pass

    @abstractmethod
    def get_user_language(self) -> Language:
        """Return the user's main language."""
        pass

    @abstractmethod
    def get_learning_language(self) -> Language:
        """Return the user's learning language."""
        pass

    @abstractmethod
    def get_profile_completed(self) -> bool:
        """Return True if the user profile is completed."""
        pass

    @abstractmethod
    def set_user_language(self, language: Language) -> None:
        """Set the user's main language."""
        pass

    @abstractmethod
    def set_learning_language(self, language: Language) -> None:
        """Set the user's learning language."""
        pass

    @abstractmethod
    def set_profile_completed(self) -> None:
        """Mark the user's profile as completed."""
        pass
