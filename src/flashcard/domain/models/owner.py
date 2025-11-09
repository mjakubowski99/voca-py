from pydantic import BaseModel
from src.flashcard.domain.value_objects import OwnerId
from src.shared.user.iuser import IUser
from src.shared.value_objects.user_id import UserId
from src.flashcard.domain.enum import FlashcardOwnerType


class Owner(BaseModel):
    id: OwnerId
    flashcard_owner_type: FlashcardOwnerType

    @classmethod
    def from_user(cls, user_id: UserId) -> "Owner":
        owner_id = OwnerId.from_string(str(user_id.value))
        return cls(id=owner_id, flashcard_owner_type=FlashcardOwnerType.USER)

    @classmethod
    def from_auth_user(cls, user: IUser) -> "Owner":
        owner_id = OwnerId.from_string(str(user.get_id().value))
        return cls(id=owner_id, flashcard_owner_type=FlashcardOwnerType.USER)

    def equals(self, owner: "Owner") -> bool:
        return (
            self.id.equals(owner.get_id()) and self.flashcard_owner_type == owner.get_owner_type()
        )

    def is_user(self) -> bool:
        return self.flashcard_owner_type == FlashcardOwnerType.USER

    def is_admin(self) -> bool:
        return self.flashcard_owner_type == FlashcardOwnerType.ADMIN
