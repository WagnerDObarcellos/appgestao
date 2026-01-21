import pytest  # type: ignore
from sqlalchemy import select  # type: ignore

from app_gestao.models import Todo, User


@pytest.mark.asyncio
async def test_create_user(db_session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test', email='test@example.com', password='secret'
        )
        db_session.add(new_user)
        await db_session.commit()

    user = await db_session.scalar(select(User).where(User.username == 'test'))

    assert user.username == 'test'
    assert user.email == 'test@example.com'
    assert user.role == 'user'
    assert user.created_at == time

    assert user.id is not None


@pytest.mark.asyncio
async def test_create_todo(db_session, user):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    db_session.add(todo)
    await db_session.commit()

    todo = await db_session.scalar(select(Todo))

    assert todo.title == 'Test Todo'
    assert todo.description == 'Test Desc'
    assert todo.state == 'draft'
    assert todo.user_id == user.id


@pytest.mark.asyncio
async def test_user_todo_relationship(db_session, user: User):
    user = await db_session.merge(user)

    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )
    db_session.add(todo)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.todos == [todo]
