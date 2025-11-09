from pydantic import BaseModel
from src.shared.flashcard.contracts import IRatingContext
from src.shared.user.iuser import IUser
from src.shared.value_objects.flashcard_id import FlashcardId
from src.study.domain.enum import Rating


class RatingContext(BaseModel, IRatingContext):
    user: IUser
    flashcard_id: FlashcardId
    rating: Rating

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def get_user(self) -> IUser:
        return self.user

    def get_flashcard_id(self) -> FlashcardId:
        return self.flashcard_id

    def get_rating(self) -> Rating:
        return self.rating
