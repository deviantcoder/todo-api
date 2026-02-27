from typing_extensions import Any

from fastapi import APIRouter

from version import __version__


router = APIRouter(tags=['root'])


@router.get('/')
async def root() -> dict[str, Any]:
    return {
        'message': 'Welcome to Test Todo API',
        'version': __version__
    }
