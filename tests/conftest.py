from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from types import SimpleNamespace

import factory  # type: ignore
import pytest_asyncio  # type: ignore
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event  # type: ignore
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlalchemy.pool import StaticPool  # type: ignore

from app_gestao.database import Base, get_session
from app_gestao.main.app import app
from app_gestao.models.user import User
from app_gestao.security import get_password_hash
from app_gestao.settings import Settings

# Configuração Global única para SQLite em memória compartilhado
engine = create_async_engine(
    'sqlite+aiosqlite://',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def db_session():
    """Fixture principal de sessão. Use este nome em todos os testes."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Cria e remove as tabelas em cada teste usando o StaticPool."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def user(db_session):
    password = 'testtest'
    user_obj = UserFactory(password=get_password_hash(password))
    db_session.add(user_obj)
    await db_session.commit()
    await db_session.refresh(user_obj)
    user_obj.clean_password = password
    return user_obj


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_via_api(client):
    payload = {
        'username': 'teste',
        'email': 'teste@test.com',
        'password': 'testtest',
    }
    # CORREÇÃO: Adicionado await para evitar erro de corrotina
    response = await client.post('/users/', json=payload)
    server_user = response.json()
    assert response.status_code == HTTPStatus.CREATED, server_user
    server_user['clean_password'] = 'testtest'
    return SimpleNamespace(**server_user)


@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 21)):
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
    response = await client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )
    assert response.status_code == HTTPStatus.OK, response.json()
    return response.json()['access_token']


@pytest_asyncio.fixture
async def other_user(db_session):
    user_obj = UserFactory(
        username='Another',
        email='another_email@example.com',
        password=get_password_hash('anotherpassword'),
    )
    db_session.add(user_obj)
    await db_session.commit()
    await db_session.refresh(user_obj)
    return user_obj


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
async def admin_user(db_session, user):
    user.role = 'admin'
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def settings_fixture():
    return Settings()
