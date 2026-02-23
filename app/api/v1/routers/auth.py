from typing import Annotated

from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select

from app.schemas.user import User, UserCreate
from app.schemas.token import Token

from app.api.dependencies import SessionDep
from app.models.user import User as UserModel
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    path='/register',
    response_model=User,
    status_code=status.HTTP_201_CREATED
)
async def register(
    session: SessionDep,
    user_data: UserCreate
) -> User:
    db_user = session.scalars(
        select(UserModel).where(UserModel.email == user_data.email)
    ).first()

    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )

    hashed_pwd = get_password_hash(user_data.password)

    user = UserModel(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pwd
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@router.post(
    path='/token',
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    db_user = session.scalars(
        select(UserModel).where(UserModel.email == form_data.username)
    ).first()

    if db_user is None or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token = create_access_token({'sub': form_data.username})

    return Token(
        access_token=access_token,
        token_type='bearer'
    )
