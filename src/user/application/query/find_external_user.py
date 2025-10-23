from src.shared.enum import UserProvider
from src.shared.value_objects.user_id import UserId
from src.shared.user.iuser import IUser
from src.user.application.dto.user_dto import UserDTO
from src.user.application.repository.contracts import IUserRepository

class FindExternalUserHandler:

    def __init__(self, repository: IUserRepository):
        self.repository = repository


    async def find(self, provider_id: str, provider_type: UserProvider) -> IUser:
        return UserDTO(
            await self.repository.find_by_provider(provider_id, provider_type)
        )
