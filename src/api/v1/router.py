from fastapi import APIRouter

from .routes import auth, task


v1_router = APIRouter(prefix='/v1')

v1_router.include_router(auth.router)
v1_router.include_router(task.router)
