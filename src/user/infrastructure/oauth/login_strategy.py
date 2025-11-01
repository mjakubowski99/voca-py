from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
from config import settings
from src.shared.enum import UserProvider
from src.user.domain.contracts import IOAuthUser
from src.user.infrastructure.oauth.models import OAuthUser
from google.auth.exceptions import GoogleAuthError, MalformedError
from typing import Optional
from abc import ABC, abstractmethod
import asyncio
import httpx
import jwt
from datetime import datetime, timedelta


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
                None, lambda: id_token.verify_oauth2_token(token, self.request, self.client_id)
            )
        except (ValueError, GoogleAuthError, MalformedError) as e:
            # ValueError: invalid token
            # GoogleAuthError: Malformed token, signature error, etc
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google ID token: {str(e)}",
            )

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to verify Google ID token"
            )

        return OAuthUser(
            id=payload["sub"],
            user_provider=UserProvider.GOOGLE,
            name=payload.get("name"),
            email=payload["email"],
            nickname=payload["email"],
            avatar=payload.get("picture"),
        )


class AppleLoginStrategy(ILoginStrategy):
    """
    Apple login strategy using authorization code (async version).
    """

    TOKEN_URL = "https://appleid.apple.com/auth/token"

    def __init__(self):
        self.client_id = settings.apple_client_id
        self.team_id = settings.apple_team_id
        self.key_id = settings.apple_key_id
        self.private_key = settings.apple_private_key
        self.redirect_uri = settings.apple_redirect_url

    def _generate_client_secret(self) -> str:
        """Generate JWT client secret for Apple token request"""
        now = datetime.utcnow()
        payload = {
            "iss": self.team_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=180)).timestamp()),
            "aud": "https://appleid.apple.com",
            "sub": self.client_id,
        }
        headers = {"kid": self.key_id}

        client_secret = jwt.encode(payload, self.private_key, algorithm="ES256", headers=headers)
        return client_secret

    async def user_from_token(self, token: str) -> OAuthUser:
        """
        Exchange authorization code for Apple ID token and extract user info.
        """
        client_secret = self._generate_client_secret()
        data = {
            "client_id": self.client_id,
            "client_secret": client_secret,
            "code": token,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        headers = {"content-type": "application/x-www-form-urlencoded"}

        async with httpx.AsyncClient() as client:
            res = await client.post(self.TOKEN_URL, data=data, headers=headers)
            if res.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Apple token request failed: {res.text}",
                )
            token_response = res.json()

        id_token = token_response.get("id_token")
        if not id_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Apple ID token not returned"
            )

        # decode token without verification (for production, verify signature using Apple keys)
        decoded = jwt.decode(id_token, options={"verify_signature": False})

        return OAuthUser(
            id=decoded.get("sub"),
            user_provider=UserProvider.APPLE,
            email=decoded.get("email"),
            name=decoded.get("name"),
            nickname=decoded.get("email"),
            avatar=None,
        )
