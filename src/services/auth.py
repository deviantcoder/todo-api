from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.core.config import settings
from src.core.exceptions import (
    AlreadyExistsException,
    EmailNotVerifiedException,
    InvalidCredentialsException,
    InvalidOperationException,
    NotFoundException,
    TokenExpiredException,
    TokenRevokedException,
)
from src.infra.caching.cache_keys import get_cache_key
from src.infra.caching.cache_manager import CacheManager
from src.infra.caching.cache_service import CacheService
from src.infra.security.auth import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    create_verification_token,
    hash_password,
    hash_refresh_token,
    hash_reset_token,
    hash_verification_token,
    verify_password,
)
from src.models.refresh_token import RefreshToken
from src.models.user import User
from src.repos.refresh_token import RefreshTokenRepository
from src.repos.user import UserRepository
from src.schemas.auth import ChangePasswordRequest, TokenResponse
from src.schemas.user import UserCreate
from src.worker.tasks import send_password_reset_email, send_verification_email, send_welcome_email


class AuthService:
    """
    Service layer for handling authentication and authorization operations.

    Manages user registration, login, token refresh, logout, password management,
    email verification, and related caching logic.

    Attributes:
        user_repo (UserRepository): Repository for user database operations.
        token_repo (RefreshTokenRepository): Repository for refresh token database operations.
        cache (CacheService): Low-level cache service for direct cache interactions.
        user_cache (CacheManager[User]): High-level cache manager for User model instances.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        cache: CacheService
    ) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.cache = cache
        self.user_cache = CacheManager[User](cache, User)

    async def register(self, data: UserCreate) -> User:
        """
        Register a new user account.
        """

        existing = await self.user_repo.get_by_username_or_email(data.username, data.email)

        if existing is not None:
            raise AlreadyExistsException('User already exists')

        hashed_pwd = hash_password(data.password)

        user = User(
            username=data.username,
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed_pwd,
            is_verified=False
        )

        created = await self.user_repo.create(user)

        raw_token, hashed_token = create_verification_token()

        key = get_cache_key('verification_token', hashed_token)

        await self.cache.set(
            key,
            {'user_id': str(created.id)},
            ttl=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60
        )

        send_welcome_email.delay(user.username, user.email, raw_token)  # type: ignore

        return created

    async def login(self, username: str, password: str) -> TokenResponse:
        """
        Authenticate a user and issue access and refresh tokens.
        """

        user = await self.user_cache.get_or_fetch(
            get_cache_key('user:username', username),
            lambda: self.user_repo.get_by_username(username),
            use_cache=True
        )

        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()

        if not user.is_verified:
            raise EmailNotVerifiedException()

        return await self._generate_tokens(user)

    async def refresh(self, raw_token: str) -> TokenResponse:
        """
        Refresh an access token using a valid refresh token.
        """

        token = await self._get_token(raw_token)

        if token is None:
            raise InvalidCredentialsException()

        if token.is_revoked:
            await self.token_repo.revoke_all_for_user(token.owner_id)
            raise TokenRevokedException()

        if token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise TokenExpiredException()

        await self.token_repo.revoke(token)

        try:
            user = await self.user_cache.get_or_fetch(
                get_cache_key('user:username', token.owner_id),
                lambda: self.user_repo.get_by_id(token.owner_id),
                use_cache=True
            )
        except Exception:
            raise InvalidCredentialsException()

        return await self._generate_tokens(user)

    async def logout(self, raw_token: str) -> None:
        """
        Revoke a single refresh token, logging the user out of the current session.
        """

        token = await self._get_token(raw_token)

        if token is None:
            raise InvalidCredentialsException()

        if token.is_revoked:
            raise TokenRevokedException()

        await self.token_repo.revoke(token)

    async def logout_all(self, user: User) -> None:
        """
        Revoke all refresh tokens for a user, logging them out of all sessions.
        """

        await self.token_repo.revoke_all_for_user(user.id)

    async def _get_token(self, raw_token: str) -> RefreshToken | None:
        """
        Look up a refresh token record by its raw value.
        """

        token_hash = hash_refresh_token(raw_token)
        return await self.token_repo.get_by_hash(token_hash)

    async def _generate_tokens(self, user: User) -> TokenResponse:
        """
        Create and persist a new access/refresh token pair for a user.
        """

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

    async def change_password(self, user: User, data: ChangePasswordRequest) -> None:
        """
        Change the authenticated user's password.
        """

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()

        if data.password == data.new_password:
            raise InvalidOperationException('New password cannot be the same as the current password')

        hashed_pwd = hash_password(data.new_password)

        await self.user_repo.update(user, {'hashed_password': hashed_pwd})
        await self.token_repo.revoke_all_for_user(user.id)

    async def forgot_password(self, email: str) -> None:
        """
        Initiate a password reset flow for a user.
        """

        user = await self.user_repo.get_by_email(email)

        if user is None:
            raise NotFoundException('User does not exist')

        raw_token, hashed_token = create_reset_token()
        key = get_cache_key('reset_token', hashed_token)

        await self.cache.set(
            key,
            {'user_id': str(user.id)},
            ttl=settings.RESET_TOKEN_EXPIRE_MINUTES * 60
        )

        send_password_reset_email.delay(user.username, user.email, raw_token)  # type: ignore

    async def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset a user's password using a valid password reset token.
        """

        hashed_token = hash_reset_token(token)
        key = get_cache_key('reset_token', hashed_token)

        data = await self.cache.get(key)

        if data is None:
            raise InvalidCredentialsException('Reset token is invalid or expired')

        user = await self.user_repo.get_by_id(UUID(data['user_id']))

        if user is None:
            raise InvalidCredentialsException()

        hashed_pwd = hash_password(new_password)

        await self.user_repo.update(user, {'hashed_password': hashed_pwd})
        await self.cache.invalidate(key)
        await self.token_repo.revoke_all_for_user(user.id)

    async def verify_email(self, token: str) -> None:
        """
        Verify a user's email address using a verification token.
        """

        hashed_token = hash_verification_token(token)
        key = get_cache_key('verification_token', hashed_token)

        data = await self.cache.get(key)

        if data is None:
            raise InvalidCredentialsException('Verification token is invalid or expired')

        user = await self.user_repo.get_by_id(UUID(data['user_id']))

        if user is None:
            raise InvalidCredentialsException()

        if user.is_verified:
            raise InvalidOperationException('Email is already verified')

        updated = await self.user_repo.update(user, {'is_verified': True})

        await self.user_cache.set(get_cache_key('user:username', updated.username), updated)
        await self.cache.invalidate(key)

    async def resend_verification(self, email: str) -> None:
        """
        Resend the email verification link to a user.
        """

        user = await self.user_repo.get_by_email(email)

        if user is None:
            raise NotFoundException('User does not exist')

        if user.is_verified:
            raise InvalidOperationException('Email is already verified')

        raw_token, hashed_token = create_verification_token()
        key = get_cache_key('verification_token', hashed_token)

        await self.cache.set(
            key,
            {'user_id': str(user.id)},
            ttl=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES * 60
        )

        send_verification_email.delay(user.username, user.email, raw_token)  # type: ignore
