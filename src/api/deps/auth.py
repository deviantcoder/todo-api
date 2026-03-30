from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from src.api.deps.user import UserRepoDep
from src.api.deps.session import SessionDep
from src.services.auth import AuthService
from src.repos.refresh_token import RefreshTokenRepository
from src.core.security import verify_access_token
from src.core.exceptions import InvalidCredentialsException
from src.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/token')


def get_refresh_token_repo(session: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


RefreshTokenRepoDep = Annotated[RefreshTokenRepository, Depends(get_refresh_token_repo)]


def get_auth_service(user_repo: UserRepoDep, token_repo: RefreshTokenRepoDep) -> AuthService:
    return AuthService(user_repo, token_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: UserRepoDep
):
    payload = verify_access_token(token)

    if payload is None:
        raise InvalidCredentialsException()

    username = payload.get('sub')

    if not username:
        raise InvalidCredentialsException()

    user = await user_repo.get_by_username(username)

    if user is None:
        raise InvalidCredentialsException()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
