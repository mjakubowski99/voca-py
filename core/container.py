import punq

from src.flashcard.application.command.generate_flashcards import GenerateFlashcardsHandler
from src.flashcard.application.query.get_deck_details import GetDeckDetails
from src.flashcard.application.query.get_decks_list import GetAdminDecks, GetUserDecks
from src.flashcard.application.repository.contracts import (
    IFlashcardDeckReadRepository,
    IFlashcardDeckRepository,
    IFlashcardDuplicateRepository,
    IFlashcardRepository,
    ISmTwoFlashcardRepository,
    IStoryRepository,
)
from src.flashcard.application.services.deck_resolver import DeckResolver
from src.flashcard.application.services.flashcard_duplicate_service import FlashcardDuplicateService
from src.flashcard.application.services.flashcard_generator_service import FlashcardGeneratorService
from src.flashcard.application.services.gemini_generator import GeminiGenerator
from src.flashcard.application.services.iflashcard_generator import IFlashcardGenerator
from src.flashcard.application.services.story_duplicate_service import StoryDuplicateService
from src.flashcard.infrastructure.repository.flashcard_deck_read_repository import (
    FlashcardDeckReadRepository,
)
from src.flashcard.infrastructure.repository.flashcard_deck_repository import (
    FlashcardDeckRepository,
)
from src.flashcard.infrastructure.repository.flashcard_duplicate_repository import (
    FlashcardDuplicateRepository,
)
from src.flashcard.infrastructure.repository.flashcard_read_repository import (
    FlashcardReadRepository,
)
from src.flashcard.infrastructure.repository.flashcard_repository import FlashcardRepository
from src.flashcard.infrastructure.repository.sm_two.criteria_factory import (
    FlashcardSortCriteriaFactory,
)
from src.flashcard.infrastructure.repository.sm_two_flashcard_repository import (
    SmTwoFlashcardRepository,
)
from src.flashcard.infrastructure.repository.story_repository import StoryRepository
from src.shared.user.iuser_facade import IUserFacade
from src.shared.util.hash import ArgonHash, IHash
from src.user.application.command.create_external_user import CreateExternalUserHandler
from src.user.application.command.create_token import CreateTokenHandler
from src.user.application.command.create_user import CreateUserHandler
from src.user.application.command.login_user import LoginUserHandler
from src.user.application.facades.user_facade import UserFacade
from src.user.application.query.find_user import FindUserHandler
from src.user.application.query.get_oauth_user import GetOAuthUser
from src.user.application.repository.contracts import ITokenRepository, IUserRepository
from src.user.domain.contracts import IOAuthLogin
from src.user.infrastructure.oauth.oauth_login import OAuthLogin
from src.user.infrastructure.repository.jwt_token_repository import JwtTokenRepository
from src.user.infrastructure.repository.user_repository import UserRepository
from config import settings
from typing import TypeVar, Type, Callable

T = TypeVar("T")


def resolve(cls: Type[T]) -> Callable[[], T]:
    """
    Universal FastAPI dependency resolver for anything registered in the container.
    Example: Depends(resolve(MyHandler))
    """

    def _resolve() -> T:
        return container.resolve(cls)

    return _resolve


container = punq.Container()

container.register(FlashcardSortCriteriaFactory)
container.register(SmTwoFlashcardRepository)
container.register(ISmTwoFlashcardRepository, SmTwoFlashcardRepository)
container.register(GetUserDecks)
container.register(GetAdminDecks)
container.register(GetDeckDetails)
container.register(IFlashcardDeckReadRepository, FlashcardDeckReadRepository)
container.register(FlashcardGeneratorService)
container.register(IFlashcardGenerator, GeminiGenerator)
container.register(DeckResolver)
container.register(GenerateFlashcardsHandler)
container.register(IFlashcardRepository, FlashcardRepository)
container.register(StoryDuplicateService)
container.register(FlashcardDuplicateService)
container.register(FlashcardRepository)
container.register(FlashcardReadRepository)
container.register(FlashcardDeckReadRepository)
container.register(FlashcardDeckRepository)
container.register(FlashcardDuplicateRepository)
container.register(IFlashcardDeckRepository, FlashcardDeckRepository)
container.register(IFlashcardDuplicateRepository, FlashcardDuplicateRepository)
container.register(IStoryRepository, StoryRepository)
container.register(CreateExternalUserHandler)
container.register(FindUserHandler)
container.register(CreateTokenHandler)
container.register(IHash, ArgonHash)
container.register(LoginUserHandler)
container.register(CreateUserHandler)
container.register(IOAuthLogin, OAuthLogin)
container.register(GetOAuthUser)
container.register(IUserRepository, UserRepository)
container.register(IUserFacade, UserFacade)
container.register(ITokenRepository, instance=JwtTokenRepository(secret_key=settings.jwt_secret))
