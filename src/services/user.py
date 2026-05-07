from uuid import UUID

from src.core.exceptions import (
    AlreadyExistsException,
    InvalidCredentialsException,
    InvalidOperationException,
)
from src.infra.caching.cache_keys import get_cache_key
from src.infra.caching.cache_manager import CacheManager
from src.infra.caching.cache_service import CacheService
from src.infra.security.auth import verify_password
from src.models.user import User
from src.repos.user import UserRepository
from src.schemas.pagination import PagedResponse, PaginationParams
from src.schemas.user import ChangeEmailRequest, ChangeUsernameRequest, UserResponse


class UserService:
    """
    Service layer for managing users.

    Attributes:
        repo (UserRepository): Repository for user data access.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        cache: CacheService
    ) -> None:
        self.user_repo = user_repo
        self.user_cache = CacheManager(cache, User)

    async def get_all(self, pg_params: PaginationParams) -> PagedResponse[UserResponse]:
        """
        Retrieve list of all users.  # TODO: update
        """

        items, total = await self.user_repo.get_all()

        return PagedResponse.create(items, total, pg_params)

    async def get_by_id(self, user_id: UUID) -> User:
        """
        Retrieve a single user by ID.
        """

        return await self.user_cache.get_or_fetch(
            get_cache_key('user:id', user_id),
            lambda: self.user_repo.get_by_id(user_id),
            use_cache=True
        )

    async def change_username(self, user: User, data: ChangeUsernameRequest) -> User:
        """
        Change the username of an existing user.
        """

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()

        if data.new_username == user.username:
            raise InvalidOperationException('New username cannot be the same as the current username')

        existing = await self.user_repo.get_by_username(data.new_username)

        if existing is not None:
            raise AlreadyExistsException('Username is already taken')

        await self.user_cache.invalidate(get_cache_key('user:id', user.id))
        await self.user_cache.invalidate(get_cache_key('user:username', user.username))

        return await self.user_repo.update(user, {'username': data.new_username})

    async def change_email(self, user: User, data: ChangeEmailRequest) -> User:
        """
        Change the email of an existing user.
        """

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()

        if data.new_email == user.email:
            raise InvalidOperationException('New email cannot be the same as the current email')

        existing = await self.user_repo.get_by_username_or_email(email=data.new_email)

        if existing is not None:
            raise AlreadyExistsException('Email is already registered')

        await self.user_cache.invalidate(get_cache_key('user:id', user.id))
        await self.user_cache.invalidate(get_cache_key('user:username', user.username))

        return await self.user_repo.update(user, {'email': data.new_email})
