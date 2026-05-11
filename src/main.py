from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src import models  # noqa
from src.api.v1.router import v1_router
from src.core.config import settings
from src.core.exceptions import AppException
from src.infra.caching.cache import connect_redis, disconnect_redis
from src.infra.logging.logger import configure_logging
from src.infra.rate_limit.limiter import limiter

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    await connect_redis()
    yield
    await disconnect_redis()

app = FastAPI(**settings.fastapi_kwargs, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True
)

app.include_router(v1_router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.detail}
    )
