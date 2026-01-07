from http import HTTPStatus

from app_gestao.schemas import UserPublic
from app_gestao.security import create_access_token


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
