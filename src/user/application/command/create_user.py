from datetime import datetime
from typing import Optional
import uuid
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, HttpUrl

from src.shared.util.hash import IHash
from src.user.application.repository.contracts import IUserRepository


class CreateUserCommand(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    email_verified_at: Optional[datetime] = Field(None, description="When the email was verified")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    password: str = Field(..., min_length=8, description="Plain password to be hashed")
    picture: Optional[HttpUrl] = Field(None, description="Profile picture URL")


class CreateUserHandler:
    def __init__(self, repository: IUserRepository, hash_service: IHash):
        self.repository = repository
        self.hash = hash_service

    async def handle(self, command: CreateUserCommand) -> None:
        # Check if user already exists
        existing_user = await self.repository.find_by_email(command.email)
        if existing_user:
            raise HTTPException(
                status_code=403,
                detail="User with this email already exists!",
            )

        # Hash password
        hashed_password = self.hash.make(command.password)

        # Persist user
        await self.repository.create({
            "id": uuid.uuid4(),
            "name": command.name,
            "email": command.email,
            "email_verified_at": command.email_verified_at,
            "password": hashed_password,
            "picture": command.picture,
            "provider_id": None,
            "provider_type": None,
        })