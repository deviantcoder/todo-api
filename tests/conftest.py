from unittest.mock import AsyncMock

import pytest

from src.repos.project import ProjectRepository
from src.repos.project_member import ProjectMemberRepository
from src.repos.refresh_token import RefreshTokenRepository
from src.repos.task import TaskRepository
from src.repos.user import UserRepository


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def task_repo() -> AsyncMock:
    return AsyncMock(spec=TaskRepository)


@pytest.fixture
def project_repo() -> AsyncMock:
    return AsyncMock(spec=ProjectRepository)


@pytest.fixture
def member_repo() -> AsyncMock:
    return AsyncMock(spec=ProjectMemberRepository)


@pytest.fixture
def token_repo() -> AsyncMock:
    return AsyncMock(spec=RefreshTokenRepository)
