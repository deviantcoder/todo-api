from fastapi import APIRouter

from src.api.deps.auth import AuthServiceDep, LoginFormDep
from src.models.user import User
from src.schemas.user import UserResponse, UserCreate
from src.schemas.auth import TokenResponse


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=UserResponse)
async def register(service: AuthServiceDep, data: UserCreate) -> User:
    return await service.register(data)


@router.post('/token', response_model=TokenResponse)
async def login(service: AuthServiceDep, form_data: LoginFormDep) -> TokenResponse:
    return await service.login(form_data.username, form_data.password)
