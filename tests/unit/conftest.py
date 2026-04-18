import pytest

from src.services.auth import AuthService
from src.services.project import ProjectService
from src.services.task import TaskService
from src.services.user import UserService
from src.services.project_member import ProjectMemberService


@pytest.fixture
def auth_service(user_repo, token_repo) -> AuthService:
    return AuthService(user_repo, token_repo)


@pytest.fixture
def user_service(user_repo) -> UserService:
    return UserService(user_repo)


@pytest.fixture
def task_service(task_repo, project_repo) -> TaskService:
    return TaskService(task_repo, project_repo)


@pytest.fixture
def project_service(project_repo, member_repo) -> ProjectService:
    return ProjectService(project_repo, member_repo)


@pytest.fixture
def member_service(member_repo, project_repo, user_repo) -> ProjectMemberService:
    return ProjectMemberService(member_repo, project_repo, user_repo)
