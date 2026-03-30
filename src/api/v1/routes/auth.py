from fastapi import APIRouter

from src.api.deps.auth import AuthServiceDep
from src.models.user import User
from src.schemas.user import UserResponse, UserCreate


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=UserResponse)
async def register(service: AuthServiceDep, data: UserCreate) -> User:
    return await service.register(data)
