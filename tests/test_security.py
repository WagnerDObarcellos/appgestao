from datetime import timedelta
from http import HTTPStatus

from jwt import decode  # type: ignore

from app_gestao.security import SECRET_KEY, create_access_token


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
