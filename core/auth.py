from fastapi import Depends, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from core.container import container
from src.shared.user.iuser import IUser
from src.shared.user.iuser_facade import IUserFacade

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="BearerAuth")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_facade: IUserFacade = Depends(lambda: container.resolve(IUserFacade)),
) -> IUser:
    try:
        user = await user_facade.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
