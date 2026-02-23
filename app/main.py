from fastapi import FastAPI

from .api.v1.router import api_router


app = FastAPI(
    title='Test Todo API',
    version='0.1.0'
)

app.include_router(api_router)
