import asyncio
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.messaging.email import send_email
from src.core.messaging.email_templates import due_date_reminder_email, welcome_email
from src.models.task import Task, TaskStatus
from src.models.user import User
from src.worker.app import celery_app

logger = logging.getLogger(__name__)


def run_async(async_func):
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))
    return wrapper


@celery_app.task(name='src.worker.tasks.send_welcome_email')
@run_async
async def send_welcome_email(username: str, email: str) -> None:
    logger.info(f'Sending welcome email to: {email}')
    await send_email(
        subject='Welcome to Todo App!',
        recipients=[email],
        body=welcome_email(username)
    )
    logger.info(f'Welcome email sent to: {email}')


@celery_app.task(name='src.worker.tasks.send_due_date_reminders')
@run_async
async def send_due_date_reminders() -> None:
    engine = create_async_engine(url=settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    tommorow = datetime.now(timezone.utc) + timedelta(days=1)
    tommorow_start = tommorow.replace(hour=0, minute=0, second=0, microsecond=0)
    tommorow_end = tommorow.replace(hour=23, minute=59, second=59, microsecond=999999)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Task, User)
            .join(User, User.id == Task.owner_id)
            .where(
                Task.status == TaskStatus.ACTIVE,
                Task.due_date >= tommorow_start,
                Task.due_date <= tommorow_end
            )
        )

        rows = result.all()

    user_tasks: dict[str, dict] = {}

    for task, user in rows:
        if user.email not in user_tasks:
            user_tasks[user.email] = {
                'username': user.username,
                'tasks': [],
            }

        user_tasks[user.email]['tasks'].append(
            {
                'title': task.title,
                'due_date': task.due_date.strftime('%Y-%m-%d %H:%M')
            }
        )

    for email, data in user_tasks.items():
        logger.info(f'Sending due date reminder email to: {email}')
        await send_email(
            subject='Tasks due tommorow',
            recipients=[email],
            body=due_date_reminder_email(data['username'], data['tasks'])  # type: ignore
        )
        logger.info(f'Reminder email sent to: {email}')
