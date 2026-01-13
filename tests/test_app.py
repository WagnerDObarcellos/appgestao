from http import HTTPStatus
from unittest.mock import patch

import pytest  # type: ignore
from fastapi import HTTPException  # type: ignore

from app_gestao.schemas import UserPublic
from app_gestao.security import (
    create_access_token,
    get_current_user,
    verify_password,
)


def test_root_deve_retornar_ola_mundo(client):

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá, mundo!'}


# CREATE USER TESTS
# test create user sucesso
def test_create_user_deve_criar_usuario(client):

    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    body = response.json()

    assert body['username'] == 'alice'
    assert body['email'] == 'alice@example.com'
    assert isinstance(body['id'], int)


# test create user email duplicado
def test_create_user_email_duplicado(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'outro',
            'email': user.email,
            'password': '123456',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


# test create user username duplicado
def test_create_user_username_duplicado(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'novo@email.com',
            'password': '123456',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


# READ USERS TESTS
# test read users deve retornar lista de usuarios
def test_read_users_deve_retornar_lista_de_usuarios(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


# test read users com query params
def test_read_users_with_query_params(client, token, user):
    response = client.get(
        '/users?skip=0&limit=1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert 'users' in data
    assert isinstance(data['users'], list)
    assert len(data['users']) <= 1


# UPDATE USER TESTS
# test update user sucesso
def test_update_user_sucesso(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'bob',
        'email': 'bob@example.com',
    }


# test update user conflito email duplicado
def test_update_user_retorar_conflito(client, user, token):
    # Criando um registro para "fausto"
    client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )
    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Email or username already exists'
    }


# test update user inexistente
def test_update_user_inexistente(client, token):
    response = client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'x',
            'email': 'x@x.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


# test update user sem token
def test_update_user_sem_token(client, user):
    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'x',
            'email': 'x@x.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_user_forbidden(client, other_user, token):
    # Testa erro 403 ao tentar atualizar outro usuário.
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'novo_nome',
            'email': 'novo_email@example.com',
            'password': 'nova_senha',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


# DELETE USER TESTS
# test delete user sucesso
def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''


# test delete user inexistente
def test_delete_user_inexistente(client, token):
    response = client.delete(
        '/users/999',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


# test delete user forbidden
def test_delete_user_forbidden(client, other_user, token):
    """Testa erro 403 ao tentar deletar outro usuário."""
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


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


# GET_CURRENT_USER_TOKEN
# teste token não encontrado
def test_get_current_user_not_found(client):
    data = {'no-email': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_get_current_user_does_not_exists(client):
    data = {'sub': 'test@test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
async def test_get_current_user_token_vazio(session):
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token='', db=session)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == 'Not authenticated'


def test_not_verify_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_verify_password_exception():
    with patch(
        'app_gestao.security.pwd_context.verify',
        side_effect=Exception('Erro interno'),
    ):
        result = verify_password('senha', 'hash_invalido')

    assert result is False


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
