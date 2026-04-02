from uuid import UUID

from src.repos.user import UserRepository
from src.models.user import User
from src.core.exceptions import (
    NotFoundException,
    InvalidCredentialsException,
    InvalidOperationException,
    AlreadyExistsException
)
from src.core.security import verify_password
from src.schemas.user import ChangeUsernameRequest, ChangeEmailRequest


class UserService:
    """
    User service class
    """

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def get_all(self) -> list[User]:
        return await self.repo.get_all()

    async def get_by_id(self, id: UUID) -> User:
        user = await self.repo.get_by_id(id)

        if user is None:
            raise NotFoundException('User not found')

        return user

    async def change_username(self, user: User, data: ChangeUsernameRequest) -> User:
        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()

        if data.new_username == user.username:
            raise InvalidOperationException('New username cannot be the same as the current username')

        existing = await self.repo.get_by_username(data.new_username)

        if existing is not None:
            raise AlreadyExistsException('Username is already taken')

        return await self.repo.update(user, {'username': data.new_username})

    async def change_email(self, user: User, data: ChangeEmailRequest) -> User:
        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException()

        if data.new_email == user.email:
            raise InvalidOperationException('New email cannot be the same as the current email')

        existing = await self.repo.get_by_username_or_email(email=data.new_email)

        if existing is not None:
            raise AlreadyExistsException('Email is already registered')

        return await self.repo.update(user, {'email': data.new_email})
