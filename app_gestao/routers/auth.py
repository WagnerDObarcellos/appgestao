from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException  # type: ignore
from fastapi.security import OAuth2PasswordRequestForm  # type: ignore
from sqlalchemy import select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app_gestao.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_user,
    verify_password,
)
from app_gestao.db.database import get_session
from app_gestao.models.user import User
from app_gestao.schemas.auth import RefreshToken, Token

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2Form, session: SessionDep):  # type: ignore
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    try:
        password_valid = verify_password(
            form_data.password,
            user.password,
        )
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not password_valid:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    # REMOVIDO 'await': create_access_token é síncrona
    access_token = create_access_token(
        data={
            'sub': str(user.id),
            'role': user.role,
        }
    )

    # REMOVIDO 'await': create_refresh_token é síncrona
    refresh_token = create_refresh_token(
        data={
            'sub': str(user.id),
            'role': user.role,  # Adicionado role para consistência no refresh
        }
    )

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
    }


@router.post('/refresh_token', response_model=Token)
async def refresh_access_token(payload: RefreshToken):
    data = decode_refresh_token(payload.refresh_token)

    if not data:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Invalid or expired refresh token',
        )

    user_id = data.get('sub')
    user_role = data.get('role', 'user')

    # REMOVIDO 'await': create_access_token é síncrona
    access_token = create_access_token(
        data={'sub': str(user_id), 'role': user_role}
    )

    return {
        'access_token': access_token,
        'refresh_token': payload.refresh_token,
        'token_type': 'bearer',
    }
