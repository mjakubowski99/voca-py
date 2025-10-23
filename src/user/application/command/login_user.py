from typing import Optional
from src.shared.user.iuser import IUser
from src.user.application.repository.contracts import IUserRepository
from src.shared.util.hash import IHash
from src.user.application.dto.user_dto import UserDTO


class LoginUserHandler:
    def __init__(self, repository: IUserRepository, hash_service: IHash):
        self.repository = repository
        self.hash = hash_service

    async def handle(self, username: str, password: str) -> Optional[IUser]:
        # async user lookup
        user = await self.repository.find_by_email(username)  # must be async

        if not user:
            return None

        if not self.hash.check(password, user.get_password()):
            return None

        return UserDTO(user)
