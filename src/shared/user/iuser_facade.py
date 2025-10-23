from abc import ABC, abstractmethod
from typing import Optional
from src.shared.user.iuser import IUser

class IUserFacade(ABC):
    
    @abstractmethod
    async def get_user_by_token(self, token: str) -> Optional[IUser]:
        pass