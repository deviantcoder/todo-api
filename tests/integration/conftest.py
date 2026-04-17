from typing import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.security import create_access_token
from src.db.base import Base
from src.db.session import get_session
from src.main import app
from src.models.project import Project
from src.models.task import Task
from src.models.user import User
from tests.factories import ProjectFactory, TaskFactory, UserFactory
from src.core.limiter import limiter

TEST_DATABASE_URL = 'sqlite+aiosqlite:///./test.db'


engine = create_async_engine(url=TEST_DATABASE_URL, connect_args={'check_same_thread': False})
TestSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(scope='session', autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def disable_rate_limiting() -> Generator:
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    user = UserFactory.build()

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def project(db_session: AsyncSession, user: User) -> Project:
    project = ProjectFactory.build(owner_id=user.id)

    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    return project


@pytest.fixture
async def task(db_session: AsyncSession, user: User, project: Project) -> Task:
    task = TaskFactory.build(owner_id=user.id, project_id=project.id)

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    return task


@pytest.fixture
def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({'sub': user.username})
    return {'Authorization': f'Bearer {token}'}
