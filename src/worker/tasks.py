import asyncio
import logging
from functools import wraps

from src.core.messaging.email import send_email
from src.core.messaging.email_templates import welcome_email
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
