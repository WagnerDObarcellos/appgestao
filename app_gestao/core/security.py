from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import Depends, HTTPException  # type: ignore
from fastapi.security import OAuth2PasswordBearer  # type: ignore
from jose import JWTError, jwt  # type: ignore
from passlib.context import CryptContext  # type: ignore
from sqlalchemy import select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app_gestao.core.settings import settings
from app_gestao.db.database import get_session
from app_gestao.models.user import User

# =========================
# CONFIG
# =========================


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Tipos reutilizáveis (Dependências)
SessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

# =========================
# PASSWORD
# =========================


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =========================
# TOKEN (SÍNCRONOS)
# =========================


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    # Em 2026, usamos timezone-aware datetimes
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({'exp': expire, 'type': 'refresh'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_refresh_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# =========================
# AUTH DEPENDENCIES (ASSÍNCRONAS)
# =========================


async def get_current_user(
    token: TokenDep,
    db_session: SessionDep,  # type: ignore
) -> User:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('sub')

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(User).where(User.id == int(user_id))
    result = await db_session.execute(query)
    user = result.scalar_one_or_none()
    result = await db_session.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception

    return user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='The user does not have enough privileges',
        )
    return current_user


async def AdminPermission(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:

    if current_user.role != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Admin privileges required',
        )
    return current_user
