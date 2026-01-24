from http import HTTPStatus

import pytest  # type: ignore

from app_gestao.core.security import create_access_token
from app_gestao.schemas import UserPublic


# CREATE USER TESTS
# test create user sucesso
@pytest.mark.asyncio
async def test_create_user_deve_criar_usuario(client):

    response = await client.post(
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
@pytest.mark.asyncio
async def test_create_user_email_duplicado(client, user):
    response = await client.post(
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
@pytest.mark.asyncio
async def test_create_user_username_duplicado(client, user):
    response = await client.post(
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
@pytest.mark.asyncio
async def test_read_users_deve_retornar_lista_de_usuarios(
    client, admin_user, db_session
):

    await db_session.commit()
    await db_session.refresh(admin_user)

    login_response = await client.post(
        '/auth/token',
        data={
            'username': admin_user.email,
            'password': admin_user.clean_password,
        },
    )

    assert login_response.status_code == HTTPStatus.OK
    token = login_response.json()['access_token']

    user_schema = UserPublic.model_validate(admin_user).model_dump()

    db_session.expire_all()

    response = await client.get(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


# test read users com query params
@pytest.mark.asyncio
async def test_read_users_with_query_params(client, admin_user, db_session):
    await db_session.commit()
    token = create_access_token(data={'sub': str(admin_user.id)})
    response = await client.get(
        '/users/?skip=0&limit=1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK


# UPDATE USER TESTS
# test update user sucesso
@pytest.mark.asyncio
async def test_update_user_sucesso(client, user, user_token):
    response = await client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.OK
    json_data = response.json()
    assert json_data['username'] == 'bob'
    assert json_data['email'] == 'bob@example.com'
    assert json_data['role'] == 'user'


# test update user conflito email duplicado
@pytest.mark.asyncio
async def test_update_user_retorar_conflito(client, user, user_token):
    # Criando um registro para "fausto"
    await client.post(
        '/users/',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )
    response_update = await client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
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
@pytest.mark.asyncio
async def test_update_user_inexistente(client, user_token):
    response = await client.put(
        '/users/999',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'username': 'x',
            'email': 'x@x.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


# test update user sem token
@pytest.mark.asyncio
async def test_update_user_sem_token(client, user):
    response = await client.put(
        f'/users/{user.id}',
        json={
            'username': 'x',
            'email': 'x@x.com',
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


@pytest.mark.asyncio
async def test_update_user_forbidden(client, other_user, user_token):
    # Testa erro 403 ao tentar atualizar outro usuário.
    response = await client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
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
@pytest.mark.asyncio
async def test_delete_user(client, user, user_token):
    response = await client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''


# test delete user inexistente
@pytest.mark.asyncio
async def test_delete_user_inexistente(client, user_token):
    response = await client.delete(
        '/users/999',
        headers={'Authorization': f'Bearer {user_token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


# test delete user forbidden
@pytest.mark.asyncio
async def test_delete_user_forbidden(client, other_user, user_token):
    """Testa erro 403 ao tentar deletar outro usuário."""
    response = await client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
