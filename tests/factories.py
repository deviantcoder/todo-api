from datetime import datetime, timedelta, timezone
from uuid import uuid4

from factory.base import Factory
from factory.declarations import LazyFunction, Sequence

from src.core.security import hash_password, hash_refresh_token
from src.models.project import Project, ProjectStatus
from src.models.refresh_token import RefreshToken
from src.models.task import Task, TaskPriority, TaskStatus
from src.models.user import User

USER_PASSWORD = 'pass123'


class UserFactory(Factory[User]):
    id = LazyFunction(uuid4)
    username = Sequence(lambda n: f'user_{n}')
    email = Sequence(lambda n: f'johndoe_{n}@gmail.com')
    full_name = 'John Doe'
    hashed_password = LazyFunction(lambda: hash_password(USER_PASSWORD))
    is_active = True

    class Meta:  # type: ignore
        model = User


class TaskFactory(Factory[Task]):
    id = LazyFunction(uuid4)
    title = Sequence(lambda n: f'Test task {n}')
    description = Sequence(lambda n: f'Test task {n} description')
    status = TaskStatus.ACTIVE
    priority = TaskPriority.LOW
    due_date = LazyFunction(lambda: datetime(2026, 12, 12))
    owner_id = LazyFunction(uuid4)
    project_id = LazyFunction(uuid4)

    class Meta:  # type: ignore
        model = Task


class ProjectFactory(Factory[Project]):
    id = LazyFunction(uuid4)
    title = Sequence(lambda n: f'Test project {n}')
    description = Sequence(lambda n: f'Test project {n} description')
    status = ProjectStatus.ACTIVE
    due_date = LazyFunction(lambda: datetime(2026, 12, 12))
    owner_id = LazyFunction(uuid4)

    class Meta:  # type: ignore
        model = Project


REFRESH_TOKEN = 'VTDtrxWiLsgZAUt8bL55pKNgWDNhFl9aF-ppsuD9IQI1W0_kGcr5V1loFb4KBOxSyjlWNhBxDf0O8vxwWFms_A'


class RefreshTokenFactory(Factory[RefreshToken]):
    id = LazyFunction(uuid4)
    hashed_token = LazyFunction(lambda: hash_refresh_token(REFRESH_TOKEN))
    expires_at = LazyFunction(lambda: datetime.now(timezone.utc) + timedelta(days=30))
    is_revoked = False
    owner_id = LazyFunction(uuid4)

    class Meta:  # type: ignore
        model = RefreshToken
