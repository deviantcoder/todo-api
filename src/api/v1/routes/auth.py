from fastapi import APIRouter, status
from fastapi.requests import Request

from src.api.deps.auth import AuthServiceDep, CurrentUserDep, LoginFormDep
from src.core.limiter import limiter
from src.models.user import User
from src.schemas.auth import (
    ChangePasswordRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from src.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit('10/minute')
async def register(
    request: Request,  # noqa
    service: AuthServiceDep,
    data: UserCreate
) -> User:
    return await service.register(data)


@router.post('/token', response_model=TokenResponse)
@limiter.limit('5/minute')
async def login(
    request: Request,  # noqa
    service: AuthServiceDep,
    form_data: LoginFormDep
) -> TokenResponse:
    return await service.login(form_data.username, form_data.password)


@router.post('/refresh', response_model=TokenResponse)
@limiter.limit('10/minute')
async def refresh(
    request: Request,  # noqa
    service: AuthServiceDep,
    data: RefreshRequest,
    current_user: CurrentUserDep  # noqa
) -> TokenResponse:
    return await service.refresh(data.refresh_token)


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    service: AuthServiceDep,
    data: LogoutRequest,
    current_user: CurrentUserDep  # noqa
) -> None:
    return await service.logout(data.refresh_token)


@router.post('/logout-all', status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(service: AuthServiceDep, current_user: CurrentUserDep) -> None:
    return await service.logout_all(current_user)


@router.post('/change-password', status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit('5/minute')
async def change_password(
    request: Request,  # noqa
    service: AuthServiceDep,
    data: ChangePasswordRequest,
    current_user: CurrentUserDep
) -> None:
    return await service.change_password(current_user, data)
