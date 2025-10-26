from abc import ABC, abstractmethod

from src.shared.value_objects.user_id import UserId
from typing import Optional
from src.shared.enum import UserProvider
from src.shared.user.iuser import IUser


class IUserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> IUser:
        """Find a user by ID. Raises exception if not found."""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[IUser]:
        """Find a user by email. Returns None if not found."""
        pass

    @abstractmethod
    async def create(self, attributes: dict) -> IUser:
        """Create a new user with the given attributes."""
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Delete a user by ID."""
        pass

    @abstractmethod
    async def exists_by_provider(self, provider_id: str, provider: UserProvider) -> bool:
        """Check if a user exists by provider ID and provider type."""
        pass

    @abstractmethod
    async def find_by_provider(self, provider_id: str, provider: UserProvider) -> IUser:
        """Find a user by provider ID and provider type. Raises exception if not found."""
        pass

    @abstractmethod
    async def update(self, user: IUser) -> None:
        """Update an existing user's fields."""
        pass


class ITokenRepository(ABC):
    @abstractmethod
    async def create(user: IUser) -> str:
        pass

    @abstractmethod
    async def verify(self, token: str) -> Optional[IUser]:
        pass
