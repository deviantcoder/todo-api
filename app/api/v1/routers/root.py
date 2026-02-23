from fastapi import APIRouter


router = APIRouter(tags=['root'])


@router.get('/')
async def root():
    return {
        'message': 'Welcome to Test Todo API',
        'version': '0.1.0'
    }
