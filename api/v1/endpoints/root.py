from fastapi import APIRouter


router = APIRouter(tags=['root'])


@router.get('/')
async def read_root():
    return {'message': 'Welcome to Todo API 🚀'}
