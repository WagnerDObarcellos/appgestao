from http import HTTPStatus
from unittest.mock import patch

import pytest  # type: ignore
from freezegun import freeze_time  # type: ignore

from app_gestao.core.security import create_access_token


@pytest.mark.asyncio
async def test_token_expired_after_time(client, user):

    with freeze_time('2026-01-20 12:00:00'):
        response = await client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        # Se falhar aqui, verifique se a fixture user deu session.commit()
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    # 3. Avançamos o tempo para invalidar o token gerado acima.
    with freeze_time('2026-01-27 12:31:00'):
        response = await client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'newname',
                'email': 'new@email.com',
                'password': 'newpassword',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        # Verifique se o detail é exatamente este:
        assert response.json()['detail'] == 'Could not validate credentials'


# TOKEN TESTS
# test get token sucesso
@pytest.mark.asyncio
async def test_get_token_sucesso(client, user):
    response = await client.post(
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
@pytest.mark.asyncio
async def test_get_token_credenciais_invalidas(client, user):
    response = await client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'senha_errada_aqui'},
    )
    body = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'access_token' not in body
    assert body['detail'] == 'Incorrect email or password'


# Teste get toke passwod verify exception
@pytest.mark.asyncio
async def test_get_token_password_verify_exception(client, user):
    with patch('app_gestao.routers.auth.verify_password') as mock:
        mock.side_effect = Exception('Erro interno de Hash')

        response = await client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Incorrect email or password'}


# teste quando o usuario não existe
@pytest.mark.asyncio
async def test_get_token_usuario_nao_existe(client):
    response = await client.post(
        '/auth/token',
        data={
            'username': 'naoexiste@email.com',
            'password': 'qualquer_senha',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


# Teste de email inexistente
@pytest.mark.asyncio
async def test_get_token_email_inexistente(client):
    response = await client.post(
        '/auth/token',
        data={
            'username': 'naoexiste@test.com',
            'password': 'qualquer-senha',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


# Teste get token senha incorreta
@pytest.mark.asyncio
async def test_get_token_senha_incorreta(client, user):
    response = await client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': 'senha-errada',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_login_token_verify_password_exception(client, user):

    with patch(
        'app_gestao.routers.auth.verify_password',
        side_effect=Exception('Erro interno'),
    ):
        response = await client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': 'senha_errada',
            },
        )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Incorrect email or password'


@pytest.mark.asyncio
async def test_not_verify_password(client, user):
    response = await client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


@pytest.mark.asyncio
async def test_refresh_token(client, user, user_token):
    refresh_token = create_access_token(
        data={'sub': str(user.id), 'role': 'user'},
    )
    response = await client.post(
        '/auth/refresh_token',
        json={'refresh_token': refresh_token},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_token_expired_dont_refresh(client, user):
    with freeze_time('2023-01-14 12:00:00'):
        response = await client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        refresh_token = response.json()['refresh_token']

    with freeze_time('2023-01-21 12:31:00'):
        response = await client.post(
            '/auth/refresh_token',
            json={'refresh_token': refresh_token},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Invalid or expired refresh token'
        }
