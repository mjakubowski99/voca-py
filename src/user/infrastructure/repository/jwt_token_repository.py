import uuid
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from src.shared.user.iuser import IUser
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId
from src.user.application.dto.user_dto import UserDTO
from src.user.application.repository.contracts import ITokenRepository
from src.user.infrastructure.models import User


class JwtTokenRepository(ITokenRepository):
    def __init__(self, secret_key: str, algorithm: str = "HS256", expires_in_minutes: int = 60):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expires_in_minutes = expires_in_minutes

    async def create(self, user: IUser) -> str:
        exp_time = datetime.now(timezone.utc) + timedelta(minutes=self.expires_in_minutes)

        payload = {
            "sub": str(user.get_id().value),
            "exp": exp_time.timestamp(),
            "iat": datetime.now(timezone.utc).timestamp(),
            "user": {
                "id": user.get_id().get_value(),
                "email": user.get_email(),
                "name": user.get_name(),
                "user_language": user.get_user_language().get_value(),
                "learning_language": user.get_learning_language().get_value(),
            },
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    async def verify(self, token: str) -> Optional[IUser]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id_str = payload.get("sub")
            if user_id_str:
                return UserDTO(
                    domain_user=User(
                        id=uuid.UUID(user_id_str),
                        email=payload["user"]["email"],
                        password="",
                        name=payload["user"]["name"],
                        learning_language=Language.from_string(
                            payload["user"]["learning_language"]
                        ),
                        user_language=Language.from_string(payload["user"]["user_language"]),
                        profile_completed=True,
                    )
                )
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
