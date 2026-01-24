import pytest  # type: ignore
from sqlalchemy import select  # type: ignore

from app_gestao.models.user import User
from app_gestao.scripts import create_admin


@pytest.mark.asyncio
async def test_create_first_admin_com_sessao_injetada(db_session):

    # Chama a função principal do script
    await create_admin.create_first_admin(db_session)

    # Verifica se o admin foi persistido no banco de teste
    stmt = select(User).where(User.email == 'admin@admin.com')
    result = await db_session.execute(stmt)
    admin = result.scalars().first()

    assert admin is not None
    assert admin.role == 'admin'
    assert admin.username == 'admin'


@pytest.mark.asyncio
async def test_create_first_admin_ja_existente(db_session):

    # Cria o primeiro admin
    await create_admin.create_first_admin(db_session)

    # Tenta criar novamente
    await create_admin.create_first_admin(db_session)

    # Verifica se ainda existe apenas um
    stmt = select(User).where(User.email == 'admin@admin.com')
    result = await db_session.execute(stmt)
    admins = result.scalars().all()

    assert len(admins) == 1
