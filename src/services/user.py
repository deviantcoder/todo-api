from uuid import UUID

from src.repos.user import UserRepository
from src.models.user import User
from src.core.exceptions import NotFoundException


class UserService:
    """
    User service class
    """

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def get_all(self) -> list[User]:
        return await self.repo.get_all()

    async def get_by_id(self, id: UUID) -> User | None:
        user = await self.repo.get_by_id(id)

        if user is None:
            raise NotFoundException('User not found')

        return user
