from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from src import models  # noqa
from src.api.v1.router import v1_router
from src.core.config import settings
from src.core.exceptions import AppException

app = FastAPI(**settings.fastapi_kwargs)

app.include_router(v1_router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={'detail': exc.detail}
    )
