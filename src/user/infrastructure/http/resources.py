from pydantic import BaseModel, Field


class UserResource(BaseModel):
    id: str = Field(..., description="User unique ID")
    name: str = Field(..., description="User full name")
    email: str = Field(..., description="User email")
    has_any_session: bool = Field(..., description="Whether the user has any active session")
    profile_completed: bool = Field(..., description="Whether the user has completed their profile")
    user_language: str = Field(..., description="The user's language code", example="pl")
    learning_language: str = Field(
        ..., description="The language the user is learning", example="en"
    )


class TokenUserResource(BaseModel):
    token: str = Field(..., description="Authentication token", example="123")
    user: UserResource = Field(..., description="User data")


class LanguageResource(BaseModel):
    code: str = Field(..., description="Language code")
    flag: str = Field(..., description="Language flag")
