from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints
from src.shared.enum import UserProvider, Platform


class OAuthLoginRequest(BaseModel):
    access_token: str = Field(..., description="External oauth service access token", example="eYjjwwawwaadasda")
    user_provider: UserProvider = Field(..., description="OAuth provider", example=UserProvider.GOOGLE.value)
    platform: Platform = Field(..., description="Client platform", example=Platform.WEB.value)

    class Config:
        use_enum_values = True  # Serialize enums as their values

class LoginRequest(BaseModel):
    username: Annotated[
        str,
        StringConstraints(
            min_length=3,
            max_length=50,
        ),
    ] = Field(..., description="Username", example="tomasz123")

    password: Annotated[
        str,
        StringConstraints(
            min_length=8,
            max_length=128,
        ),
    ] = Field(..., description="Password", example="password123")