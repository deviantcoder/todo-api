from fastapi import APIRouter, status

from src.api.deps.auth import (
    AuthServiceDep,
    LoginFormDep,
    CurrentUserDep
)
from src.models.user import User
from src.schemas.user import UserResponse, UserCreate
from src.schemas.auth import (
    TokenResponse,
    RefreshRequest,
    LogoutRequest,
    ChangePasswordRequest
)


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=UserResponse)
async def register(service: AuthServiceDep, data: UserCreate) -> User:
    return await service.register(data)


@router.post('/token', response_model=TokenResponse)
async def login(service: AuthServiceDep, form_data: LoginFormDep) -> TokenResponse:
    return await service.login(form_data.username, form_data.password)


@router.post('/refresh', response_model=TokenResponse)
async def refresh(
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
async def change_password(
    service: AuthServiceDep,
    data: ChangePasswordRequest,
    current_user: CurrentUserDep
) -> None:
    return await service.change_password(current_user, data)
