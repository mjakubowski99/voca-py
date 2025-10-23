from pydantic import BaseModel, EmailStr
from typing import Optional
from src.shared.enum import UserProvider
from src.user.domain.contracts import IOAuthUser

class OAuthUser(BaseModel, IOAuthUser):
    id: str
    user_provider: UserProvider
    name: Optional[str] = None
    email: EmailStr
    nickname: Optional[str] = None
    avatar: Optional[str] = None

    def get_id(self) -> str:
        return self.id

    def get_user_provider(self) -> UserProvider:
        return self.user_provider

    def get_name(self) -> Optional[str]:
        return self.name

    def get_email(self) -> str:
        return self.email

    def get_nickname(self) -> Optional[str]:
        return self.nickname

    def get_avatar(self) -> Optional[str]:
        return self.avatar

    class Config:
        use_enum_values = True
        from_attributes = True
