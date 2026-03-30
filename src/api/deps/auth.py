from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.deps.user import UserRepoDep
from src.api.deps.session import SessionDep
from src.services.auth import AuthService
from src.repos.refresh_token import RefreshTokenRepository


def get_refresh_token_repo(session: SessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(session)


RefreshTokenRepoDep = Annotated[RefreshTokenRepository, Depends(get_refresh_token_repo)]


def get_auth_service(user_repo: UserRepoDep, token_repo: RefreshTokenRepoDep) -> AuthService:
    return AuthService(user_repo, token_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
