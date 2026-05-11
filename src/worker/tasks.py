import asyncio
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import settings
from src.infra.messaging.email import send_email
from src.infra.messaging.email_templates import (
    due_date_reminder_email,
    password_reset_email,
    welcome_email,
    email_change_verification_email
)
from src.models.task import Task, TaskStatus
from src.models.user import User
from src.worker.app import celery_app
from src.models.refresh_token import RefreshToken

logger = logging.getLogger(__name__)


def run_async(async_func):
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))
    return wrapper


@celery_app.task(name='src.worker.tasks.send_welcome_email')
@run_async
async def send_welcome_email(username: str, email: str, token: str) -> None:
    logger.info(f'Sending welcome email to: {email}')

    await send_email(
        subject='Welcome to Todo App!',
        recipients=[email],
        body=welcome_email(username, token)
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


@celery_app.task(name='src.worker.tasks.send_password_reset_email')
@run_async
async def send_password_reset_email(username: str, email: str, reset_token: str) -> None:
    logger.info(f'Sending password reset email to: {email}')

    await send_email(
        subject='Password Reset Request',
        recipients=[email],
        body=password_reset_email(username, reset_token)
    )

    logger.info(f'Password reset email sent to: {email}')


@celery_app.task(name='src.worker.tasks.send_verification_email')
@run_async
async def send_verification_email(username: str, email: str, token: str) -> None:
    await send_email(
        subject='Verify your email address',
        recipients=[email],
        body=welcome_email(username, token)
    )


@celery_app.task(name='src.worker.tasks.cleanup_refresh_tokens')
@run_async
async def cleanup_refresh_tokens() -> None:
    engine = create_async_engine(url=settings.DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
        await session.commit()

@celery_app.task(name='src.worker.tasks.send_email_change_verification')
@run_async
async def send_email_change_verification(username: str, new_email: str, token: str) -> None:
    await send_email(
        subject='Confirm your new email address',
        recipients=[new_email],
        body=email_change_verification_email(username, new_email, token)
    )
