from uuid import UUID

from src.core.exceptions import (
    AlreadyExistsException,
    InvalidCredentialsException,
    InvalidOperationException,
    NotFoundException,
)
from src.infra.security.auth import verify_password
from src.models.user import User
from src.repos.user import UserRepository
from src.schemas.user import ChangeEmailRequest, ChangeUsernameRequest


class UserService:
    """
    Service layer for managing users.

    Attributes:
        repo (UserRepository): Repository for user data access.
    """

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def get_all(self) -> list[User]:
        """
        Retrieve list of all users.
        """

        return await self.repo.get_all()

    async def get_by_id(self, id: UUID) -> User:
        """
        Retrieve a single user by ID.
        """

        user = await self.repo.get_by_id(id)

        if user is None:
            raise NotFoundException('User not found')

        return user

    async def change_username(self, user: User, data: ChangeUsernameRequest) -> User:
        """
        Change the username of an existing user.
        """

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()

        if data.new_username == user.username:
            raise InvalidOperationException('New username cannot be the same as the current username')

        existing = await self.repo.get_by_username(data.new_username)

        if existing is not None:
            raise AlreadyExistsException('Username is already taken')

        return await self.repo.update(user, {'username': data.new_username})

    async def change_email(self, user: User, data: ChangeEmailRequest) -> User:
        """
        Change the email of an existing user.
        """

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()

        if data.new_email == user.email:
            raise InvalidOperationException('New email cannot be the same as the current email')

        existing = await self.repo.get_by_username_or_email(email=data.new_email)

        if existing is not None:
            raise AlreadyExistsException('Email is already registered')

        return await self.repo.update(user, {'email': data.new_email})
