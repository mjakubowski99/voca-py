
from src.user.domain.contracts import IOAuthLogin, IOAuthUser
from src.shared.enum import UserProvider, Platform

class GetOAuthUser:

    def __init__(self, login: IOAuthLogin):
        self.login_service = login

    async def login(self, provider: UserProvider, token: str, platform: Platform) -> IOAuthUser:
        return await self.login_service.login(provider, token, platform)