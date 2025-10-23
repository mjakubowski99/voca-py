from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, EmailStr, HttpUrl
from src.shared.enum import UserProvider
from datetime import datetime
from pwdlib import PasswordHash
import secrets
import string
import uuid

from src.shared.util.hash import IHash
from src.user.application.repository.contracts import IUserRepository


def random_string(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits  # a-zA-Z0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class CreateExternalUser(BaseModel):
    provider_id: str
    provider_type: UserProvider
    email: EmailStr
    name: str
    picture: Optional[HttpUrl]

    class Config:
        use_enum_values = True  # Serialize enums as their values
        frozen = True           # Make the model immutable like a value object


class CreateExternalUserHandler:
    def __init__(self, repository: IUserRepository, hash: IHash):
        self.repository = repository
        self.hash = hash

    async def handle(self, command: CreateExternalUser) -> None:
        exists = await self.repository.exists_by_provider(
            provider_id=command.provider_id,
            provider=command.provider_type
        )

        if not exists:
            password = self.hash.make(random_string(16))
            await self.repository.create({
                "id": uuid.uuid4(),
                "name": command.name,
                "email": command.email,
                "email_verified_at": datetime.utcnow(),
                "password": password,
                "picture": command.picture,  # Or None if you want to ignore
                "provider_id": command.provider_id,
                "provider_type": command.provider_type,
            })
