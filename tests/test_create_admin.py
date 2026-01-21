from unittest.mock import AsyncMock, patch

import pytest  # type: ignore
from sqlalchemy import select  # type: ignore

from app_gestao.models import User
from app_gestao.scripts import create_admin


@pytest.mark.asyncio
async def test_create_first_admin_com_sessao_injetada(db_session):
    """Cobre o caminho 'else' (quando a sessão é passada pelo teste)."""
    await create_admin.create_first_admin(db_session)

    # Verifica se o admin foi persistido no banco de teste
    stmt = select(User).where(User.email == 'admin@admin.com')
    result = await db_session.execute(stmt)
    admin = result.scalars().first()

    assert admin is not None
    assert admin.role == 'admin'
    assert admin.username == 'admin'


@pytest.mark.asyncio
async def test_create_first_admin_sem_sessao_injetada():
    """Cobre o caminho 'if session is None' usando Mocks."""
    mock_session = AsyncMock()

    async def mock_get_session():
        yield mock_session

    path_gs = 'app_gestao.scripts.create_admin.get_session'
    path_lg = 'app_gestao.scripts.create_admin._logic'

    with patch(path_gs, return_value=mock_get_session()):
        with patch(path_lg, new_callable=AsyncMock) as mock_logic:
            await create_admin.create_first_admin(session=None)
            mock_logic.assert_called_once_with(mock_session)


@pytest.mark.asyncio
async def test_logic_criacao_sucesso(db_session):
    """Cobre a função _logic e garante o commit."""
    await create_admin._logic(db_session)

    stmt = select(User).where(User.username == 'admin')
    user = await db_session.scalar(stmt)
    assert user is not None
    assert user.role == 'admin'
