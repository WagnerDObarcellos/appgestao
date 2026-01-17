from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace

import factory  # type: ignore
import pytest_asyncio  # type: ignore
from fastapi.testclient import TestClient  # type: ignore
from sqlalchemy import event  # type: ignore
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool  # type: ignore

from app_gestao.app import app
from app_gestao.database import get_session
from app_gestao.models import User, table_registry
from app_gestao.security import get_password_hash
from app_gestao.settings import Settings

TEST_DATABASE_URL = 'sqlite+aiosqlite:///./test.db'


@pytest_asyncio.fixture
async def client(session):
    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    return user


@pytest_asyncio.fixture
async def user_via_api(client):
    payload = {
        'username': 'teste',
        'email': 'teste@test.com',
        'password': 'testtest',
    }

    response = client.post('/users/', json=payload)

    server_user = response.json()

    assert response.status_code == HTTPStatus.CREATED, server_user

    server_user['clean_password'] = 'testtest'

    return SimpleNamespace(**server_user)


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest_asyncio.fixture
async def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.OK, response.json()

    return response.json()['access_token']


@pytest_asyncio.fixture
async def other_user(session):
    user = UserFactory(
        username='Another',
        email='another_email@example.com',
        password=get_password_hash('anotherpassword'),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def settings():
    return Settings()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


@pytest_asyncio.fixture
async def admin_user(session, user):
    user.role = 'admin'
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()
