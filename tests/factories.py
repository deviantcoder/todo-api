from datetime import datetime
from uuid import uuid4

from factory.base import Factory
from factory.declarations import Sequence, LazyFunction

from src.models.user import User
from src.models.task import Task, TaskStatus, TaskPriority
from src.models.project import Project, ProjectStatus
from src.core.security import hash_password


class UserFactory(Factory):
    username = Sequence(lambda n: f'user_{n}')
    email = Sequence(lambda n: f'johndoe_{n}@gmail.com')
    full_name = 'John Doe'
    hashed_password = LazyFunction(lambda: hash_password('pass123'))
    is_active = True

    class Meta:  # type: ignore
        model = User


class TaskFactory(Factory):
    title = Sequence(lambda n: f'Test task {n}')
    description = Sequence(lambda n: f'Test task {n} description')
    status = TaskStatus.ACTIVE
    priority = TaskPriority.LOW
    due_date = LazyFunction(lambda: datetime(2026, 12, 12))
    owner_id = LazyFunction(uuid4)
    project_id = LazyFunction(uuid4)

    class Meta:  # type: ignore
        model = Task


class ProjectFactory(Factory):
    title = Sequence(lambda n: f'Test project {n}')
    description = Sequence(lambda n: f'Test project {n} description')
    status = ProjectStatus.ACTIVE
    due_date = LazyFunction(lambda: datetime(2026, 12, 12))
    owner_id = LazyFunction(uuid4)

    class Meta:  # type: ignore
        model = Project
