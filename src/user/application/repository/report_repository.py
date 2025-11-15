from abc import ABC, abstractmethod
from typing import Optional
from src.shared.value_objects.user_id import UserId


class IReportRepository(ABC):
    @abstractmethod
    async def create(
        self,
        type: str,
        description: str,
        email: Optional[str],
        user_id: Optional[UserId],
        reportable_id: Optional[str],
        reportable_type: Optional[str],
    ) -> int:
        """Create a new report and return its ID."""
        pass

    @abstractmethod
    async def detach_from_user(self, user_id: UserId) -> None:
        """Detach reports from a user (set user_id to None)."""
        pass
