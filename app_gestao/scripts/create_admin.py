import asyncio

from sqlalchemy import select  # type: ignore

from app_gestao.core.security import get_password_hash
from app_gestao.db.database import AsyncSessionLocal
from app_gestao.models.user import User

ADMIN_EMAIL = 'admin@admin.com'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'


async def create_first_admin(session=None):
    # Se uma sessão foi passada (via teste), usamos ela.
    # Caso contrário, criamos uma nova usando o gerenciador de contexto.
    if session is None:
        async with AsyncSessionLocal() as new_session:
            await _run_logic(new_session)
    else:
        await _run_logic(session)


async def _run_logic(session):
    """Lógica centralizada de criação para evitar redefinição de variáveis."""
    admin = await session.scalar(select(User).where(User.email == ADMIN_EMAIL))

    if admin:
        print('⚠️ Admin já existe.')
        return

    admin = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=get_password_hash(ADMIN_PASSWORD),
        role='admin',
    )

    session.add(admin)
    await session.commit()

    print('✅ Admin criado com sucesso!')
    print('📧 Email:', ADMIN_EMAIL)
    print('🔑 Senha:', ADMIN_PASSWORD)


if __name__ == '__main__':
    asyncio.run(create_first_admin())
