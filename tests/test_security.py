from datetime import timedelta
from http import HTTPStatus
from typing import Annotated
from unittest.mock import patch

import pytest  # type: ignore
from fastapi import Depends, HTTPException  # type: ignore
from jose import jwt  # type: ignore
from jwt import decode  # type: ignore

from app_gestao.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_current_user,
    verify_password,
)
from app_gestao.core.settings import Settings
from app_gestao.models.user import User

CurrentUser = Annotated[User, Depends(get_current_user)]


def create_access_token_com_expire_delta():
    settings = Settings()

    token = create_access_token(
        data={'sub': 'test@test.com'},
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert payload['sub'] == 'test@test.com'
    assert 'exp' in payload


def test_jwt():
    data = {'sub': 'testuser'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])

    assert decoded['sub'] == 'testuser'
    assert 'exp' in decoded


def test_jwt_com_expiracao_customizada():
    data = {'sub': 'testuser'}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))

    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_jwt_invalid_token(client):
    response = await client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_get_current_user_sucesso(db_session, user):
    user = await db_session.merge(user)

    await db_session.commit()

    token = create_access_token(data={'sub': str(user.id)})
    returned_user = await get_current_user(token=token, db_session=db_session)

    assert returned_user.email == user.email
    assert returned_user.id == user.id


async def get_current_admin_user(
    current_user: CurrentUser,
):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )
    return current_user


@pytest.mark.asyncio
async def test_get_current_user_token_vazio(db_session):
    # Testa o 'if not token'
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token='', db_session=db_session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Could not validate credentials'


@pytest.mark.asyncio
async def test_get_current_user_token_invalido(db_session):
    # Testa o bloco 'except JWTError'
    with pytest.raises(HTTPException) as exc:
        await get_current_user(
            token='token-totalmente-invalido', db_session=db_session
        )

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Could not validate credentials'


@pytest.mark.asyncio
async def test_get_current_user_payload_sem_email(db_session):
    # Testa um token válido, mas sem o campo 'sub' (email)
    token = jwt.encode(
        {'outro_campo': 'valor'}, SECRET_KEY, algorithm=ALGORITHM
    )

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db_session=db_session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Could not validate credentials'


@pytest.mark.asyncio
async def test_get_current_user_usuario_nao_encontrado(db_session):
    # Testa um token com e-mail que não existe no banco de dados
    # Isso cobre o 'if user is None'
    token = create_access_token(data={'sub': '99999'})

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db_session=db_session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Could not validate credentials'


# VERIFY_PASSWORD
def test_verify_password_exception():
    with patch(
        'app_gestao.core.security.pwd_context.verify',
        side_effect=Exception('Erro interno'),
    ):
        with pytest.raises(Exception, match='Erro interno'):
            verify_password('senha', 'hash_invalido')

    assert True


# GET_CURRENT_USER
# teste get_current user não encontrado
@pytest.mark.asyncio
async def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = await client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_get_current_user_does_not_exists(client):
    data = {'sub': '99999'}
    token = create_access_token(data)

    response = await client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@pytest.mark.asyncio
async def test_get_current_admin_user_forbidden(user):
    # Testa a negação (403) para usuário comum
    user.role = 'user'
    with pytest.raises(HTTPException) as exc:
        await get_current_admin_user(current_user=user)

    assert exc.value.status_code == HTTPStatus.FORBIDDEN
    # Ajuste a mensagem abaixo:
    assert exc.value.detail == 'Not enough permissions'


@pytest.mark.asyncio
async def test_get_current_admin_user_success(user):
    # Testa o retorno de sucesso para admin
    user.role = 'admin'
    result = await get_current_admin_user(current_user=user)
    assert result.role == 'admin'


@pytest.mark.asyncio
async def test_get_current_user_token_sem_sub(db_session):
    # Criamos um token válido, mas sem a chave 'sub'
    token = create_access_token(data={'some_other_key': 'no_email'})

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db_session=db_session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Could not validate credentials'
