import punq

from src.flashcard.application.facades.flashcard_facade import FlashcardFacade
from src.flashcard.application.services.flashcard_poll_manager import FlashcardPollManager
from src.flashcard.application.services.flashcard_poll_resolver import FlashcardPollResolver
from src.flashcard.application.services.flashcard_poll_updater import FlashcardPollUpdater
from src.flashcard.application.services.iflashcard_selector import IFlashcardSelector
from src.flashcard.application.services.irepetition_algorithm import IRepetitionAlgorithm
from src.shared.flashcard.contracts import IFlashcardFacade
from src.study.application.command.add_next_learning_step_handler import AddNextLearningStepHandler
from src.study.application.command.answer_exercise import AnswerExercise
from src.study.application.command.create_session import CreateSessionHandler
from src.study.application.command.rate_flashcard import RateFlashcard
from src.study.application.repository.contracts import (
    ISessionRepository,
    IUnscrambleWordExerciseRepository,
)
from src.study.infrastructure.repository.session_repository import LearningSessionRepository
from src.study.infrastructure.repository.unscramble_word_exercise_repository import (
    UnscrambleWordExerciseRepository,
)
from src.flashcard.application.command.generate_flashcards import GenerateFlashcardsHandler
from src.flashcard.application.query.get_deck_details import GetDeckDetails
from src.flashcard.application.query.get_decks_list import GetAdminDecks, GetUserDecks
from src.flashcard.application.repository.contracts import (
    IFlashcardDeckReadRepository,
    IFlashcardDeckRepository,
    IFlashcardDuplicateRepository,
    IFlashcardPollRepository,
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
from src.flashcard.application.services.sm_two.sm_two_flashcard_selector import (
    SmTwoFlashcardSelector,
)
from config import settings
from typing import TypeVar, Type, Callable
from src.flashcard.infrastructure.repository.flashcard_poll_repository import (
    FlashcardPollRepository,
)
from src.flashcard.application.services.sm_two.sm_two_repetition_algorithm import (
    SmTwoRepetitionAlgorithm,
)
from src.study.application.services.exercise_factory import ExerciseFactory
from src.study.infrastructure.repository.word_match_exercise_repository import (
    WordMatchExerciseRepository,
)
from src.study.application.repository.contracts import IWordMatchExerciseRepository
from src.study.application.command.skip_exercise import SkipExercise

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

container.register(GenerateFlashcardsHandler)
container.register(UnscrambleWordExerciseRepository)
container.register(LearningSessionRepository)
container.register(ISessionRepository, LearningSessionRepository)

container.register(IFlashcardFacade, FlashcardFacade)
container.register(IFlashcardSelector, SmTwoFlashcardSelector)
container.register(IFlashcardPollRepository, FlashcardPollRepository)
container.register(IRepetitionAlgorithm, SmTwoRepetitionAlgorithm)
container.register(FlashcardPollUpdater)
container.register(FlashcardPollManager)
container.register(FlashcardPollResolver)
container.register(CreateSessionHandler)
container.register(FlashcardFacade)
container.register(AddNextLearningStepHandler)
container.register(ExerciseFactory)
container.register(IUnscrambleWordExerciseRepository, UnscrambleWordExerciseRepository)
container.register(RateFlashcard)
container.register(WordMatchExerciseRepository)
container.register(IWordMatchExerciseRepository, WordMatchExerciseRepository)
container.register(AnswerExercise)
container.register(SkipExercise)
