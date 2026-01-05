from http import HTTPStatus

from app_gestao.schemas import UserPublic


def test_root_deve_retornar_ola_mundo(client):

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá, mundo!'}


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
    response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_users_deve_retornar_lista_de_usuarios(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user_deve_atualizar_usuario(client, user):
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


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.content == b''


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


def test_update_user_inexistente(client):
    response = client.put(
        '/users/999',
        json={
            'username': 'x',
            'email': 'x@x.com',
            'password': '123',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_conflito(client, user):
    client.post(
        '/users/',
        json={
            'username': 'outro',
            'email': 'outro@email.com',
            'password': '123',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        json={
            'username': 'outro',
            'email': user.email,
            'password': '123',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email or username already exists'}


def test_delete_user_inexistente(client):
    response = client.delete('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
