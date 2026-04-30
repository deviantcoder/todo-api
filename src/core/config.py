from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.version import __version__


class Settings(BaseSettings):
    """
    Application settings class
    """

    APP_TITLE: str = 'Todo API'
    DESCRIPTION: str = 'FastAPI Todo API'
    VERSION: str = __version__

    DATABASE_URL: str = 'sqlite+aiosqlite:///./todo.db'
    TEST_DATABASE_URL: str
    ALEMBIC_DATABASE_URL: str = 'sqlite:///./todo.db'

    REDIS_URL: str = 'redis://localhost:6379'

    CELERY_BROKER_URL: str = 'amqp://admin:admin@localhost:5672//'
    CELERY_RESULT_BACKEND: str = 'redis://localhost:6379/1'

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True

    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_ALGORITHM: str = 'HS256'

    PAGINATION_LIMIT: int = 10

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

    @property
    def fastapi_kwargs(self) -> dict:
        return {
            'title': self.APP_TITLE,
            'version': self.VERSION,
            'description': self.DESCRIPTION,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
