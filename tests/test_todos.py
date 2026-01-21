from http import HTTPStatus

import factory.fuzzy  # type: ignore
import pytest  # type: ignore

from app_gestao.models import Todo, TodoState


# TESTE CRIAÇÃO TODOS
# função para cria endpoint '/todos'
@pytest.mark.asyncio
async def test_create_todo(client, token):
    response = await client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
        },
    )
    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
    }


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    db_session, client, user, token
):
    expected_todos = 5

    todos = TodoFactory.create_batch(5, user_id=user.id)
    db_session.add_all(todos)
    await db_session.commit()

    response = await client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()
    

    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    db_session, user, client, token
):
    expected_todos = 2
    db_session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await db_session.commit()

    response = await client.get(
        '/todos/?skip=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    db_session, user, client, token
):
    expected_todos = 5
    todos = TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    db_session.add_all(todos)
    await db_session.commit()

    response = await client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    db_session, user, client, token
):
    expected_todos = 5
    todos = TodoFactory.create_batch(
        5, user_id=user.id, description='description'
    )
    db_session.add_all(todos)
    await db_session.commit()

    response = await client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    db_session, user, client, token
):
    expected_todos = 5
    todos = TodoFactory.create_batch(5, user_id=user.id, state=TodoState.draft)
    db_session.add_all(todos)
    await db_session.commit()

    response = await client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    db_session, user, client, token
):
    expected_todos = 5
    todos = TodoFactory.create_batch(
        5,
        user_id=user.id,
        title='Test todo combined',
        description='combined description',
        state=TodoState.done,
    )
    db_session.add_all(todos)

    db_session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )
    await db_session.commit()

    response = await client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert len(data['todos']) == expected_todos


@pytest.mark.asyncio
async def test_patch_todo_error(client, token):
    response = await client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_patch_todo(db_session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    db_session.add(todo)
    await db_session.commit()

    response = await client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'
