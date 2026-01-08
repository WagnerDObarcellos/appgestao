from datetime import timedelta
from http import HTTPStatus

from jose import jwt  # type: ignore
from jwt import decode  # type: ignore

from app_gestao.security import SECRET_KEY, create_access_token
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
