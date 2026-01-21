import pytest  # type: ignore
from fastapi import status  # type: ignore

from app_gestao.core.security import get_current_user_role
from app_gestao.main.app import app


@pytest.mark.asyncio
async def test_create_task_success(client):
    """Testa se uma task é criada com os campos obrigatórios."""
    payload = {
        'title': 'Minha Tarefa',
        'description': 'Descrição detalhada',
        'created_by': 1,
    }
    response = await client.post('/tasks/', json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['title'] == 'Minha Tarefa'
    assert data['status'] == 'pending'


@pytest.mark.asyncio
async def test_update_assigned_to_as_admin(client):  # Remova 'app' daqui
    """Teste de permissão de admin."""
    target_user_id = 2

    # Use o app importado diretamente
    app.dependency_overrides[get_current_user_role] = lambda: 'admin'

    try:
        res_create = await client.post(
            '/tasks/', json={'title': 'Task Admin', 'created_by': 1}
        )
        task_id = res_create.json()['id']

        response = await client.patch(
            f'/tasks/{task_id}', json={'assigned_to': target_user_id}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['assigned_to'] == target_user_id

    finally:
        # SEMPRE limpe os overrides para não afetar outros testes
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_assigned_to_as_user_forbidden(client):
    """Testa se usuário comum é bloqueado ao atribuir responsável."""
    # Mockando a função para retornar user comum
    app.dependency_overrides[get_current_user_role] = lambda: 'user'

    # 1. Cria a task
    res_create = await client.post(
        '/tasks/', json={'title': 'Task User', 'created_by': 1}
    )
    task_id = res_create.json()['id']

    # 2. Tenta atribuir responsável (Deve falhar)
    response = await client.patch(f'/tasks/{task_id}', json={'assigned_to': 2})
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'apenas administradores' in response.json()['detail']
