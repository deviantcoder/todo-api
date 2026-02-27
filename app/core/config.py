from typing import Any

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)

from version import __version__


class Settings(BaseSettings):
    TITLE: str = 'Todo API'
    VERSION: str = __version__

    DEBUG: bool = False

    DOCS_URL: str = '/docs'
    REDOC_URL: str = '/redoc'

    DATABASE_URL: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        return {
            'title': self.TITLE,
            'version': self.VERSION,
            'docs_url': self.DOCS_URL,
            'redoc_url': self.REDOC_URL
        }


settings = Settings()
