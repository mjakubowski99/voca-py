from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4
from src.shared.user.iuser import IUser
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId


class User(BaseModel, IUser):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: EmailStr
    password: str
    profile_completed: bool = False
    user_language: Language
    learning_language: Language

    model_config = {"arbitrary_types_allowed": True}

    # Methods equivalent to PHP model
    def get_id(self) -> UserId:
        return UserId.from_string(self.id)

    def get_name(self) -> str:
        return self.name

    def get_password(self) -> str:
        return self.password

    def get_email(self) -> str:
        return self.email

    def get_profile_completed(self) -> bool:
        return self.profile_completed

    def get_user_language(self) -> Language:
        return self.user_language

    def get_learning_language(self) -> Language:
        return self.learning_language

    def set_user_language(self, language: Language) -> None:
        self.user_language = language

    def set_learning_language(self, language: Language) -> None:
        self.learning_language = language

    def set_profile_completed(self) -> None:
        self.profile_completed = True
