from celery import Celery
from src.core.config import settings

celery_app = Celery(
    'todo',
    broker='amqp://admin:admin@localhost:5672//',
    backend=settings.CELERY_RESULT_BACKEND,
    include=['src.worker.tasks']
)

celery_app.autodiscover_tasks(['src.worker'])
