from http import HTTPStatus

import factory  # type: ignore
import factory.fuzzy  # type: ignore
import pytest  # type: ignore

from app_gestao.core.security import get_session
from app_gestao.main.app import app
from app_gestao.models.todo import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('sentence')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_create_todo(client, user, user_token, db_session):
    app.dependency_overrides[get_session] = lambda: db_session

    try:
        response = await client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {user_token}'},
            json={
                'title': 'Test todo',
                'description': 'Test todo description',
                'state': 'draft',
            },
        )

        assert response.status_code == HTTPStatus.CREATED

        data = response.json()
        assert data['title'] == 'Test todo'
        assert data['description'] == 'Test todo description'
        assert data['state'] == 'draft'
        assert 'id' in data

    finally:
        app.dependency_overrides.clear()
