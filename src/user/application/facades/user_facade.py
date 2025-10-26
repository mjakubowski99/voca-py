from typing import Optional
from src.shared.user.iuser import IUser
from src.shared.user.iuser_facade import IUserFacade
from src.user.application.repository.contracts import ITokenRepository, IUserRepository
from src.user.application.dto.user_dto import UserDTO


class UserFacade(IUserFacade):
    def __init__(self, user_repository: IUserRepository, token_repository: ITokenRepository):
        self.user_repository = user_repository
        self.token_repository = token_repository

    async def get_user_by_token(self, token: str) -> Optional[IUser]:
        return await self.token_repository.verify(token)
