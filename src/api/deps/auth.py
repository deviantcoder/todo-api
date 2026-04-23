from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.api.deps.cache import CacheServiceDep
from src.api.deps.repos import UserRepoDep
from src.api.deps.session import SessionDep
from src.core.cache_keys import user_key_by_username
from src.core.exceptions import InvalidCredentialsException
from src.core.security import verify_access_token
from src.models.user import User
from src.repos.refresh_token import RefreshTokenRepository
from src.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/v1/auth/token')


def get_refresh_token_repo(session: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


RefreshTokenRepoDep = Annotated[RefreshTokenRepository, Depends(get_refresh_token_repo)]


def get_auth_service(
    user_repo: UserRepoDep,
    token_repo: RefreshTokenRepoDep,
    cache: CacheServiceDep
) -> AuthService:
    return AuthService(user_repo, token_repo, cache)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: UserRepoDep,
    cache: CacheServiceDep
):
    payload = verify_access_token(token)

    if payload is None:
        raise InvalidCredentialsException()

    username = payload.get('sub')

    if not username:
        raise InvalidCredentialsException()

    user_key = user_key_by_username(username)
    cached = await cache.get(user_key)

    if cached:
        user = User(**cached)
    else:
        user = await user_repo.get_by_username(username)
        if user:
            await cache.set(user_key, user.to_dict())

    if user is None:
        raise InvalidCredentialsException()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
