from datetime import timedelta
from http import HTTPStatus

import pytest  # type: ignore
from fastapi import HTTPException  # type: ignore
from jose import jwt  # type: ignore
from jwt import decode  # type: ignore

from app_gestao.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    get_current_user,
)
from app_gestao.settings import Settings


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


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
async def test_get_current_user_sucesso(session, user):
    # Testa o fluxo de sucesso: token válido e usuário existente
    token = create_access_token(data={'sub': user.email})
    returned_user = await get_current_user(token=token, db=session)

    assert returned_user.email == user.email
    assert returned_user.id == user.id


@pytest.mark.asyncio
async def test_get_current_user_token_vazio(session):
    # Testa o 'if not token'
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token='', db=session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Not authenticated'


@pytest.mark.asyncio
async def test_get_current_user_token_invalido(session):
    # Testa o bloco 'except JWTError'
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token='token-totalmente-invalido', db=session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Not authenticated'


@pytest.mark.asyncio
async def test_get_current_user_payload_sem_email(session):
    # Testa um token válido, mas sem o campo 'sub' (email)
    token = jwt.encode(
        {'outro_campo': 'valor'}, SECRET_KEY, algorithm=ALGORITHM
    )

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db=session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Not authenticated'


@pytest.mark.asyncio
async def test_get_current_user_usuario_nao_encontrado(session):
    # Testa um token com e-mail que não existe no banco de dados
    # Isso cobre o 'if user is None'
    token = create_access_token(data={'sub': 'naoexiste@test.com'})

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db=session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Not authenticated'
