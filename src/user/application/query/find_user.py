from src.shared.enum import UserProvider
from src.shared.value_objects.user_id import UserId
from src.user.application.repository.contracts import IUser
from src.user.application.repository.contracts import IUserRepository


class FindUserHandler:
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    async def find_external_user(self, provider_id: str, provider_type: UserProvider) -> IUser:
        return await self.repository.find_by_provider(provider_id, provider_type)

    async def find_user(self, user_id: UserId) -> IUser:
        return await self.repository.find_by_id(user_id)
