from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


app = FastAPI(**settings.fastapi_kwargs)

app.include_router(api_router)
