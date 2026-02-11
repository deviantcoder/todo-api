from fastapi import FastAPI

from api.v1.router import api_router


app = FastAPI(
    title='Todo API',
    description='A modern task & project management API',
    version='0.1.0',
    docs_url='/docs',
    redoc_url='/redoc'
)


app.include_router(api_router)
