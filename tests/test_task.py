from http import HTTPStatus
from types import SimpleNamespace

import pytest  # type: ignore

from app_gestao.core.security import AdminPermission, get_current_user
from app_gestao.main.app import app
from app_gestao.models.user import User


@pytest.mark.asyncio
async def test_create_task_success(client):
    """Testa se uma task é criada com os campos obrigatórios."""
    payload = {
        'title': 'Minha Tarefa',
        'description': 'Descrição detalhada',
        'created_by': 1,
    }
    response = await client.post('/tasks/', json=payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['title'] == 'Minha Tarefa'
    assert data['status'] == 'pending'


@pytest.mark.asyncio
async def test_update_assigned_to_as_admin(client):  # Remova 'app' daqui
    """Teste de permissão de admin."""
    mock_admin = SimpleNamespace(id=1, email='admin@admin.com', role='admin')

    # Use o app importado diretamente
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    # Se você também tiver a dependência AdminPermission direta:
    app.dependency_overrides[AdminPermission] = lambda: mock_admin

    try:
        res_create = await client.post(
            '/tasks/', json={'title': 'Task Admin', 'created_by': 1}
        )
        task_id = res_create.json()['id']

        response = await client.patch(
            f'/tasks/{task_id}', json={'assigned_to': mock_admin.id}
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json()['assigned_to'] == mock_admin.id
    finally:
        # SEMPRE limpe os overrides para não afetar outros testes
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_assigned_to_as_user_forbidden(client):
    fake_user = User(
        id=1,
        username='user',
        email='user@test.com',
        role='user',
    )
    app.dependency_overrides[get_current_user] = lambda: fake_user

    # 1. Cria a task
    res_create = await client.post(
        '/tasks/', json={'title': 'Task User', 'created_by': 1}
    )
    task_id = res_create.json()['id']

    # 2. Tenta atribuir responsável (Deve falhar)
    response = await client.patch(f'/tasks/{task_id}', json={'assigned_to': 2})
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert 'Admin privileges required' in response.json()['detail']
    app.dependency_overrides.clear()


async def test_task_requires_admin(client, admin_token):
    response = await client.post(
        '/tasks/',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'title': 'Task Admin', 'created_by': 1},
    )

    assert response.status_code == HTTPStatus.CREATED
