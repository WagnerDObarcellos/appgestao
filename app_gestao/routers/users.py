from http import HTTPStatus
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException  # type: ignore
from sqlalchemy import select  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app_gestao.database import get_session
from app_gestao.models import User
from app_gestao.schemas import FilterPage, UserList, UserPublic, UserSchema
from app_gestao.security import get_current_user, get_password_hash

SessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_session)]


router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(
    user: UserSchema,
    session: SessionDep,
):  # type: ignore
    db_user = await session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists',
            )
        elif db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList)
async def read_users(
    params: Annotated[FilterPage, Depends()],
    session: SessionDep,  # type: ignore
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await session.scalars(
        select(User).offset(params.skip).limit(params.limit)
    )
    users = result.all()
    return {'users': users}


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: SessionDep,  # type: ignore
    current_user: Annotated[User, Depends(get_current_user)],
):

    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)
        await session.commit()
        await session.refresh(db_user)

        return db_user

    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email or username already exists',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_user(
    user_id: int,
    session: SessionDep,  # type: ignore
    current_user: Annotated[User, Depends(get_current_user)],
):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted'}
