from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from src.shared.enum import UserProvider
from src.user.domain.contracts import IOAuthUser
from src.user.infrastructure.oauth.models import OAuthUser
from google.auth.exceptions import GoogleAuthError, MalformedError
from typing import Optional
from abc import ABC, abstractmethod
import asyncio

class ILoginStrategy(ABC):

    @abstractmethod
    async def user_from_token(self, token: str) -> IOAuthUser:
        pass 


class GoogleLoginStrategy:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.request = requests.Request()

    async def user_from_token(self, token: str) -> OAuthUser:
        loop = asyncio.get_running_loop()
        
        try:
            payload: Optional[dict] = await loop.run_in_executor(
                None,
                lambda: id_token.verify_oauth2_token(token, self.request, self.client_id)
            )
        except (ValueError, GoogleAuthError, MalformedError) as e:
            # ValueError: invalid token
            # GoogleAuthError: Malformed token, signature error, etc
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google ID token: {str(e)}"
            )

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to verify Google ID token"
            )

        return OAuthUser(
            id=payload["sub"],
            user_provider=UserProvider.GOOGLE,
            name=payload.get("name"),
            email=payload["email"],
            nickname=payload["email"],
            avatar=payload.get("picture"),
        )
