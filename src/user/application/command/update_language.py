from dataclasses import dataclass
from src.shared.flashcard.contracts import IFlashcardFacade
from src.shared.value_objects.language import Language
from src.shared.value_objects.user_id import UserId
from src.user.application.dto.user_dto import UserDTO
from src.user.application.repository.contracts import IUserRepository
from src.user.infrastructure.repository.user_repository import UserModel


@dataclass(frozen=True)
class UpdateLanguage:
    user_id: UserId
    user_language: Language
    learning_language: Language


class UpdateLanguageHandler:
    def __init__(
        self,
        user_repository: IUserRepository,
        flashcard_facade: IFlashcardFacade,
    ):
        self.user_repository = user_repository
        self.flashcard_facade = flashcard_facade

    async def handle(self, command: UpdateLanguage) -> None:
        # Get the user
        user = await self.user_repository.find_by_id(command.user_id)

        user_model = UserModel(
            id=user.get_id().get_value(),
            name=user.get_name(),
            email=user.get_email(),
            password=user.get_password(),
            profile_completed=user.get_profile_completed(),
            user_language=command.user_language,
            learning_language=command.learning_language,
        )

        # Save changes
        await self.user_repository.update(user_model)

        # Clear flashcard poll after language update
        await self.flashcard_facade.post_language_update(UserDTO(user_model))
