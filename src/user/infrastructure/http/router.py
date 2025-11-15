from ast import List
from fastapi import Depends, HTTPException
from fastapi import Body
from fastapi import APIRouter
from punq import Container
from core.auth import get_current_user
from core.container import get_container
from core.generics import ResponseWrapper
from src.shared.user.iuser import IUser
from src.shared.value_objects.language import Language
from src.user.application.command.create_external_user import (
    CreateExternalUser,
    CreateExternalUserHandler,
)
from src.user.application.command.create_token import CreateTokenHandler
from src.user.application.command.delete_user import DeleteUserHandler
from src.user.application.command.login_user import LoginUserHandler
from src.user.application.command.update_language import UpdateLanguageHandler
from src.user.application.dto.user_dto import UserDTO
from src.user.application.query.find_user import FindUserHandler
from src.user.application.query.get_oauth_user import GetOAuthUser
from src.user.infrastructure.http.requests import (
    DeleteUserRequest,
    LoginRequest,
    OAuthLoginRequest,
    UpdateLanguageRequest,
)
from src.user.infrastructure.http.resources import LanguageResource, TokenUserResource, UserResource

router = APIRouter()


@router.post("/api/v2/login", response_model=ResponseWrapper[TokenUserResource])
async def login(
    request: LoginRequest = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[TokenUserResource]:
    login_user: LoginUserHandler = container.resolve(LoginUserHandler)
    create_token: CreateTokenHandler = container.resolve(CreateTokenHandler)

    user = await login_user.handle(request.username, request.password)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return ResponseWrapper[TokenUserResource](
        data=TokenUserResource(
            token=await create_token.handle(UserDTO(user)),
            user=UserResource(
                id=user.get_id().get_value(),
                name=user.get_name(),
                email=user.get_email(),
                has_any_session=False,
                profile_completed=user.get_profile_completed(),
                user_language=user.get_user_language().get_value(),
                learning_language=user.get_learning_language().get_value(),
            ),
        )
    )


@router.get("/api/user/me", response_model=ResponseWrapper[UserResource])
async def current(
    user: IUser = Depends(get_current_user),
    container: Container = Depends(get_container),
) -> ResponseWrapper[UserResource]:
    find_user: FindUserHandler = container.resolve(FindUserHandler)
    user = await find_user.find_user(user.get_id())

    return ResponseWrapper[UserResource](
        data=UserResource(
            id=user.get_id().get_value(),
            name=user.get_name(),
            email=user.get_email(),
            has_any_session=False,
            profile_completed=user.get_profile_completed(),
            user_language=user.get_user_language().get_value(),
            learning_language=user.get_learning_language().get_value(),
        )
    )


@router.post("/api/user/oauth/login", response_model=ResponseWrapper[TokenUserResource])
async def oauth_login(
    request: OAuthLoginRequest = Body(...),
    container: Container = Depends(get_container),
) -> ResponseWrapper[TokenUserResource]:
    create_external_user: CreateExternalUserHandler = container.resolve(CreateExternalUserHandler)
    find_user: FindUserHandler = container.resolve(FindUserHandler)
    get_oauth_user: GetOAuthUser = container.resolve(GetOAuthUser)
    create_token: CreateTokenHandler = container.resolve(CreateTokenHandler)

    oauth_user = await get_oauth_user.login(
        request.user_provider, request.access_token, request.platform
    )

    command = CreateExternalUser(
        provider_id=oauth_user.get_id(),
        provider_type=oauth_user.get_user_provider(),
        email=oauth_user.get_email(),
        name=oauth_user.get_email(),
        picture=None,
    )

    await create_external_user.handle(command)

    user = await find_user.find_external_user(command.provider_id, command.provider_type)

    return ResponseWrapper[TokenUserResource](
        data=TokenUserResource(
            token=await create_token.handle(UserDTO(user)),
            user=UserResource(
                id=user.get_id().get_value(),
                name=user.get_name(),
                email=user.get_email(),
                has_any_session=False,
                profile_completed=user.get_profile_completed(),
                user_language=user.get_user_language().get_value(),
                learning_language=user.get_learning_language().get_value(),
            ),
        )
    )


@router.get("/api/v2/languages")
async def get_languages() -> ResponseWrapper[LanguageResource]:
    return ResponseWrapper[LanguageResource](
        data=[
            LanguageResource(
                code=lang.get_value(),
                flag=f"https://api.vocasmart.pl/assets/flags/{lang.get_value().lower()}.svg",
            )
            for lang in Language.all()
        ]
    )


@router.delete("/api/v2/user/me", tags=["User"])
async def delete_user(
    user: IUser = Depends(get_current_user),
    request: DeleteUserRequest = Body(...),
    container: Container = Depends(get_container),
) -> dict:
    delete_user_handler: DeleteUserHandler = container.resolve(DeleteUserHandler)

    from src.user.application.command.delete_user import DeleteUser

    command = DeleteUser(user_id=user.get_id(), email=request.email)

    await delete_user_handler.handle(command)

    return {}


@router.put("/api/v2/user/me/language", tags=["User"])
async def update_language(
    user: IUser = Depends(get_current_user),
    request: UpdateLanguageRequest = Body(...),
    container: Container = Depends(get_container),
) -> dict:
    update_language_handler: UpdateLanguageHandler = container.resolve(UpdateLanguageHandler)

    from src.user.application.command.update_language import UpdateLanguage
    from src.shared.value_objects.language import Language

    command = UpdateLanguage(
        user_id=user.get_id(),
        user_language=Language(request.user_language),
        learning_language=Language(request.learning_language),
    )

    await update_language_handler.handle(command)

    return {}
