from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select

from schemas.user import UserOut, UserCreate
from schemas.token import Token

from api.dependencies import SessionDep
from models.user import User
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


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


@router.post(
    path='/login',
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login(
    db: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user = db.scalars(
        select(User).where(User.email == form_data.username)
    ).first()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.email}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type='bearer'
    )
