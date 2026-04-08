from unittest.mock import MagicMock
from datetime import datetime, timezone

import pytest

from src.core.exceptions import (
    AlreadyExistsException,
    InvalidCredentialsException,
    TokenRevokedException,
    TokenExpiredException
)
from src.core.security import hash_refresh_token
from src.schemas.user import UserCreate
from src.services.auth import AuthService
from tests.factories import UserFactory, RefreshTokenFactory, REFRESH_TOKEN

USER_PASSWORD = 'pass123'


def make_user_create(**kwargs) -> UserCreate:
    return UserCreate(
        username=kwargs.get('username', 'johndoe'),
        email=kwargs.get('email', 'johndoe@example.com'),
        full_name=kwargs.get('full_name', 'John Doe'),
        password=USER_PASSWORD
    )


class TestRegister:
    async def test_success(self, auth_service, user_repo):
        user_repo.get_by_username_or_email.return_value = None
        user_repo.create.return_value = UserFactory.build(username='johndoe')

        result = await auth_service.register(make_user_create())

        user_repo.create.assert_called_once()
        assert result.username == 'johndoe'

    async def test_raises_if_already_exists(self, auth_service, user_repo):
        user_repo.get_by_username_or_email.return_value = UserFactory.build()

        with pytest.raises(AlreadyExistsException):
            await auth_service.register(make_user_create())

        user_repo.create.assert_not_called()


class TestLogin:
    async def test_success(self, auth_service, user_repo, token_repo):
        user = UserFactory.build()
        user_repo.get_by_username.return_value = user

        result = await auth_service.login(user.username, USER_PASSWORD)

        token_repo.create.assert_called_once()
        assert result.access_token is not None
        assert result.refresh_token is not None

    async def test_raises_if_user_not_found(self, auth_service, user_repo):
        user_repo.get_by_username.return_value = None

        with pytest.raises(InvalidCredentialsException):
            await auth_service.login('nobody', USER_PASSWORD)

    async def test_raises_if_wrong_password(self, auth_service, user_repo):
        user = UserFactory.build()
        user_repo.get_by_username.return_value = user

        with pytest.raises(InvalidCredentialsException):
            await auth_service.login(user.username, 'password')


class TestLogout:
    async def test_success(self, auth_service, token_repo):
        token = MagicMock()
        token.is_revoked = False
        token_repo.get_by_hash.return_value = token

        await auth_service.logout('sometoken')

        token_repo.revoke.assert_called_once_with(token)

    async def test_raises_if_token_not_found(self, auth_service, token_repo):
        token_repo.get_by_hash.return_value = None

        with pytest.raises(InvalidCredentialsException):
            await auth_service.logout('sometoken')

    async def test_raises_if_token_already_revoked(self, auth_service, token_repo):
        token = MagicMock()
        token.is_revoked = True
        token_repo.get_by_hash.return_value = token

        with pytest.raises(TokenRevokedException):
            await auth_service.logout('sometoken')


class TestRefresh:
    async def test_success(self, user_repo, token_repo, auth_service: AuthService):
        user = UserFactory.build()
        token = RefreshTokenFactory.build(owner_id=user.id)

        token_repo.get_by_hash.return_value = token
        user_repo.get_by_id.return_value = user

        result = await auth_service.refresh(REFRESH_TOKEN)

        token_repo.create.assert_called_once()
        assert result.access_token is not None
        assert result.refresh_token is not None

    async def test_raises_if_none(self, token_repo, auth_service: AuthService):
        token_repo.get_by_hash.return_value = None

        with pytest.raises(InvalidCredentialsException):
            await auth_service.refresh(raw_token='sometoken')

    async def test_raises_if_revoked(self, token_repo, auth_service: AuthService):
        user = UserFactory.build()
        token = RefreshTokenFactory.build(owner_id=user.id, is_revoked=True)

        token_repo.get_by_hash.return_value = token

        with pytest.raises(TokenRevokedException):
            await auth_service.refresh(REFRESH_TOKEN)

    async def test_raises_if_expired(self, token_repo, auth_service: AuthService):
        user = UserFactory.build()
        token = RefreshTokenFactory.build(
            owner_id=user.id,
            expires_at=datetime(2025, 12, 12, tzinfo=timezone.utc)
        )

        token_repo.get_by_hash.return_value = token

        with pytest.raises(TokenExpiredException):
            await auth_service.refresh(REFRESH_TOKEN)

    async def test_raises_if_not_owner(self, user_repo, token_repo, auth_service: AuthService):
        token = RefreshTokenFactory.build()

        token_repo.get_by_hash.return_value = token
        user_repo.get_by_id.return_value = None

        with pytest.raises(InvalidCredentialsException):
            await auth_service.refresh(REFRESH_TOKEN)
