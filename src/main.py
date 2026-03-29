from fastapi import FastAPI

from src import models  # noqa
from src.core.config import settings


app = FastAPI(**settings.fastapi_kwargs)
