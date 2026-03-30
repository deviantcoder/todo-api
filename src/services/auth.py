from src.repos.user import UserRepository
from src.schemas.user import UserCreate
from src.models.user import User
from src.core.exceptions import AlreadyExistsException
from src.core.security import hash_password


class AuthService:
    """
    Auth service class
    """

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

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
