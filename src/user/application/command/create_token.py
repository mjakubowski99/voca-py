from src.shared.user.iuser import IUser
from src.shared.value_objects.user_id import UserId
from src.user.application.repository.contracts import ITokenRepository


class CreateTokenHandler:
    def __init__(self, repository: ITokenRepository):
        self.repository = repository

    async def handle(self, user: IUser) -> str:
        """
        Generate a token for the given user ID.
        """
        return await self.repository.create(user)
