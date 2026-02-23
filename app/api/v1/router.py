from fastapi import APIRouter

from .routers import root, auth, tasks


api_router = APIRouter(prefix='/v1')

api_router.include_router(root.router)
api_router.include_router(auth.router)
api_router.include_router(tasks.router)
