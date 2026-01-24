from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus

import factory  # type: ignore
import pytest  # type: ignore
import pytest_asyncio  # type: ignore
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event  # type: ignore
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlalchemy.pool import StaticPool  # type: ignore

from app_gestao.core.security import get_password_hash
from app_gestao.db.database import Base, get_session
from app_gestao.main.app import app
from app_gestao.models.user import User

# ---------- DATABASE (SQLite em memória compartilhada) ----------

engine = create_async_engine(
    'sqlite+aiosqlite://',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


# ---------- CLIENT ----------


@pytest_asyncio.fixture
async def client(db_session):
    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------- USERS ----------


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@test.com')
    password = factory.LazyFunction(lambda: get_password_hash('testtest'))
    role = 'user'


@pytest_asyncio.fixture
async def user(db_session):
    password_plana = '123456'
    user = User(
        email='test@test.com',
        username='test',
        password=get_password_hash(password_plana),
        role='user',
    )
    user.clean_password = password_plana  # type: ignore
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_token(client, user):
    response = await client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.OK, response.json()
    return response.json()['access_token']


@pytest.fixture
def fastapi_app():
    return app


@pytest.fixture(autouse=True)
def override_db_session(fastapi_app, db_session):
    fastapi_app.dependency_overrides[get_session] = lambda: db_session
    yield
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session):
    """Cria um usuário com role de admin para os testes."""
    password_plana = 'admin123'
    user = User(
        username='admin',
        email='admin@test.com',
        password=get_password_hash(password_plana),
        role='admin',
    )
    # Adiciona a senha em texto puro para o teste poder fazer login
    user.clean_password = password_plana

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def other_user(db_session):
    user = UserFactory(
        username='Another',
        email='another_email@example.com',
        password=get_password_hash('anotherpassword'),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


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
async def admin_token(client, admin_user):
    # Faz o login real para garantir que o token seja válido
    response = await client.post(
        '/auth/token',
        data={
            'username': admin_user.email,
            'password': admin_user.clean_password,
        },
    )
    return response.json()['access_token']
