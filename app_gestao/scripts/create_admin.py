import asyncio

from app_gestao.database import get_session
from app_gestao.models import User
from app_gestao.security import get_password_hash


async def create_first_admin(session=None):
    # Se uma sessão for passada (pelo teste), usamos ela.
    # Se não (pelo terminal), abrimos uma nova.
    if session is None:
        async for db_session in get_session():
            await _logic(db_session)
            break
    else:
        await _logic(session)


async def _logic(session):
    admin = User(
        username='admin',
        email='admin@admin.com',
        password=get_password_hash('admin123'),
        role='admin',
    )
    session.add(admin)
    await session.commit()
    print('✅ Admin criado com sucesso!')


if __name__ == '__main__':
    asyncio.run(create_first_admin())
