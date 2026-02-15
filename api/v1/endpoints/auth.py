from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from sqlalchemy import select

from schemas.user import UserOut, UserCreate
from api.dependencies import SessionDep
from models.user import User
from core.security import get_password_hash


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    path='/register',
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
async def register(
    db: SessionDep,
    user_in: UserCreate
):
    stmt = select(User).where(User.email == user_in.email)
    existing_user = db.scalars(stmt).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )

    hashed_password = get_password_hash(user_in.password)

    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
