from fastapi import Depends, HTTPException
from fastapi import Body
from fastapi import Depends
from fastapi import APIRouter

from config import settings
from src.entry.auth import get_current_user
from src.entry.container import container
from src.entry.db import get_session
from src.shared.user.iuser import IUser
from src.user.application.command.create_external_user import (
    CreateExternalUser,
    CreateExternalUserHandler,
)
from src.user.application.command.create_token import CreateTokenHandler
from src.user.application.command.login_user import LoginUserHandler
from src.user.application.query.find_external_user import FindExternalUserHandler
from src.user.application.query.get_oauth_user import GetOAuthUser
from src.user.infrastructure.http.requests import LoginRequest, OAuthLoginRequest
from src.user.infrastructure.http.resources import TokenUserResource, UserResource

router = APIRouter()

@router.post("/api/user/login")
async def login(
    request: LoginRequest = Body(...),
    login_user: LoginUserHandler = Depends(lambda: container.resolve(LoginUserHandler)),
    create_token: CreateTokenHandler = Depends(lambda: container.resolve(CreateTokenHandler)),
) -> TokenUserResource:
    user = await login_user.handle(request.username, request.password)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenUserResource(
        token=await create_token.handle(user.get_id()),
        user=UserResource(
            id=user.get_id().get_value(),
            name=user.get_name(),
            email=user.get_email(),
            has_any_session=False,
            profile_completed=user.profile_completed(),
            user_language=user.get_user_language().get_value(),
            learning_language=user.get_learning_language().get_value(),
        )
    )
    

@router.get("/api/user/me")
async def current(user: IUser = Depends(get_current_user)):
    return UserResource(
        id=user.get_id().get_value(),
        name=user.get_name(),
        email=user.get_email(),
        has_any_session=False,
        profile_completed=user.profile_completed(),
        user_language=user.get_user_language().get_value(),
        learning_language=user.get_learning_language().get_value(),
    )

@router.post("/api/user/oauth/login")
async def oauth_login(
    request: OAuthLoginRequest = Body(...),
    create_external_user: CreateExternalUserHandler = Depends(lambda: container.resolve(CreateExternalUserHandler)),
    find_external_user: FindExternalUserHandler = Depends(lambda: container.resolve(FindExternalUserHandler)),
    get_oauth_user: GetOAuthUser = Depends(lambda: container.resolve(GetOAuthUser)),
    create_token: CreateTokenHandler = Depends(lambda: container.resolve(CreateTokenHandler)),
):
    oauth_user = await get_oauth_user.login(request.user_provider, request.access_token, request.platform)

    command = CreateExternalUser(
        provider_id=oauth_user.get_id(),
        provider_type=oauth_user.get_user_provider(),
        email=oauth_user.get_email(),
        name=oauth_user.get_email(),
        picture=None
    )

    await create_external_user.handle(command)

    user = await find_external_user.find(command.provider_id, command.provider_type)

    return TokenUserResource(
        token=await create_token.handle(user.get_id()),
        user=UserResource(
            id=user.get_id().get_value(),
            name=user.get_name(),
            email=user.get_email(),
            has_any_session=False,
            profile_completed=user.profile_completed(),
            user_language=user.get_user_language().get_value(),
            learning_language=user.get_learning_language().get_value(),
        )
    )