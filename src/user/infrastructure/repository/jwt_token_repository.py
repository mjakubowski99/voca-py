import jwt
from datetime import datetime, timedelta
from typing import Optional
from src.shared.value_objects.user_id import UserId
from abc import ABC, abstractmethod
from src.user.application.repository.contracts import ITokenRepository


class JwtTokenRepository(ITokenRepository):
    def __init__(self, secret_key: str, algorithm: str = "HS256", expires_in_minutes: int = 60):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_in_minutes = expires_in_minutes

    async def create(self, user_id: UserId) -> str:
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=self.expires_in_minutes),
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    async def verify(self, token: str) -> Optional[UserId]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id_str = payload.get("sub")
            if user_id_str:
                return UserId.from_string(user_id_str)
            return None
        except jwt.ExpiredSignatureError:
            # Token expired
            return None
        except jwt.InvalidTokenError:
            # Invalid token
            return None