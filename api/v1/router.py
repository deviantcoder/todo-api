from fastapi import APIRouter

from .endpoints import root, tasks


api_router = APIRouter(prefix='/v1')

api_router.include_router(root.router)
api_router.include_router(tasks.router)
