from http import HTTPStatus

from app_gestao.schemas import UserPublic
from app_gestao.security import create_access_token


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
def test_read_users_deve_retornar_lista_de_usuarios(
    client, admin_user, token, session
):
    user_schema = UserPublic.model_validate(admin_user).model_dump()
    session.expire_all()
    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
    )
    if response.status_code == HTTPStatus.FORBIDDEN:
        print(f'DEBUG: Token usado para o email: {admin_user.email}')
        print(f'DEBUG: Resposta da API: {response.json()}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


# test read users com query params
def test_read_users_with_query_params(client, admin_user):
    token = create_access_token(data={'sub': admin_user.email})
    response = client.get(
        '/users?skip=0&limit=1',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK


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
    json_data = response.json()
    assert json_data['username'] == 'bob'
    assert json_data['email'] == 'bob@example.com'
    assert json_data['role'] == 'user'


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
