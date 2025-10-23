from src.shared.enum import Platform, UserProvider
from src.user.domain.contracts import IOAuthLogin, IOAuthUser
from src.user.infrastructure.oauth.login_strategy import GoogleLoginStrategy, ILoginStrategy
from config import settings
from fastapi import HTTPException, status

class OAuthLogin(IOAuthLogin):

    async def login(self, provider: UserProvider, token: str, platform: Platform) -> IOAuthUser:
        strategy = await self.get_strategy(provider, platform)

        return await strategy.user_from_token(token)

    async def get_strategy(self, provider: UserProvider, platform: Platform) -> ILoginStrategy:
        if provider == UserProvider.GOOGLE and platform == Platform.WEB:
            return GoogleLoginStrategy(settings.google_ios_client_id)
        if provider == UserProvider.GOOGLE and platform == Platform.ANDROID:
            return GoogleLoginStrategy(settings.google_android_client_id)
        if provider == UserProvider.GOOGLE and platform == Platform.IOS:
            return GoogleLoginStrategy(settings.google_android_client_id)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth login for provider {provider.value} on {platform.value} is not supported"
        )

        