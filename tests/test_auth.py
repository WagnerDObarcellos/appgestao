from http import HTTPStatus
from unittest.mock import patch

from freezegun import freeze_time  # type: ignore


# Testando a expirção do token
def test_token_expired_after_time(client, user):
    with freeze_time('2023-01-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-01-14 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}


# TOKEN TESTS
# test get token sucesso
def test_get_token_sucesso(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in body
    assert body['token_type'] == 'bearer'


# test get token credenciais invalidas
def test_get_token_credenciais_invalidas(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'senha_errada_aqui'},
    )
    body = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'access_token' not in body
    assert body['detail'] == 'Incorrect email or password'


# Teste get toke passwod verify exception
def test_get_token_password_verify_exception(client, user):
    with patch('app_gestao.routers.auth.verify_password') as mock:
        mock.side_effect = Exception('Erro interno de Hash')

        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Incorrect email or password'}


# teste quando o usuario não existe
def test_get_token_usuario_nao_existe(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'naoexiste@email.com',
            'password': 'qualquer_senha',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


# Teste de email inexistente
def test_get_token_email_inexistente(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'naoexiste@test.com',
            'password': 'qualquer-senha',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


# Teste get token senha incorreta
def test_get_token_senha_incorreta(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'senha-errada',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_token_verify_password_exception(client, user):
    """
    Se verify_password lançar exceção,
    a rota deve responder 401 e não quebrar a aplicação.
    """

    with patch(
        'app_gestao.routers.auth.verify_password',
        side_effect=Exception('Erro interno'),
    ):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': 'senha_errada',
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Incorrect email or password'


def test_not_verify_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token(client, user, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2023-01-14 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-01-14 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Not authenticated'}
