import punq

from src.shared.user.iuser_facade import IUserFacade
from src.shared.util.hash import ArgonHash, IHash
from src.user.application.command.create_external_user import CreateExternalUserHandler
from src.user.application.command.create_token import CreateTokenHandler
from src.user.application.command.create_user import CreateUserHandler
from src.user.application.command.login_user import LoginUserHandler
from src.user.application.facades.user_facade import UserFacade
from src.user.application.query.find_external_user import FindExternalUserHandler
from src.user.application.query.get_oauth_user import GetOAuthUser
from src.user.application.repository.contracts import ITokenRepository, IUserRepository
from src.user.domain.contracts import IOAuthLogin
from src.user.infrastructure.oauth.oauth_login import OAuthLogin
from src.user.infrastructure.repository.jwt_token_repository import JwtTokenRepository
from src.user.infrastructure.repository.user_repository import UserRepository 
from config import settings

container = punq.Container()

container.register(CreateExternalUserHandler)
container.register(FindExternalUserHandler)
container.register(CreateTokenHandler)
container.register(IHash, ArgonHash)
container.register(LoginUserHandler)
container.register(CreateUserHandler)
container.register(IOAuthLogin, OAuthLogin)
container.register(GetOAuthUser)
container.register(IUserRepository, UserRepository)
container.register(IUserFacade, UserFacade)
container.register(ITokenRepository, instance=JwtTokenRepository(
    secret_key=settings.jwt_secret
))