from datetime import datetime, timedelta, timezone

from src.repos.user import UserRepository
from src.repos.refresh_token import RefreshTokenRepository
from src.schemas.user import UserCreate
from src.schemas.auth import TokenResponse
from src.models.user import User
from src.models.refresh_token import RefreshToken
from src.core.exceptions import (
    AlreadyExistsException,
    InvalidCredentialsException
)
from src.core.security import (
    hash_password,
    create_access_token,
    create_refresh_token
)
from src.core.config import settings


class AuthService:
    """
    Auth service class
    """

    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def register(self, data: UserCreate) -> User:
        existing = await self.user_repo.get_by_username_or_email(data.username, data.password)

        if existing is not None:
            raise AlreadyExistsException('User already exists')

        hashed_pwd = hash_password(data.password)

        user = User(
            username=data.username,
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed_pwd
        )

        return await self.user_repo.create(user)

    async def login(self, username: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_username(username)

        if user is None:
            raise InvalidCredentialsException()

        return await self._generate_tokens(user)

    async def _generate_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(payload={'sub': user.username})
        raw_refresh, hashed_refresh = create_refresh_token()

        refresh_token = RefreshToken(
            hashed_token=hashed_refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            owner_id=user.id
        )

        await self.token_repo.create(refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh
        )
