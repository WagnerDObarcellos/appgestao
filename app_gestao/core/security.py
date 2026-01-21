from typing import Annotated

from fastapi import Depends  # type: ignore


# Em um sistema real, aqui você buscaria o usuário do banco ou JWT
async def get_current_user_role() -> str:
    """Simula a obtenção do cargo do usuário logado."""
    return 'user'  # Poderia ser "admin" ou "user"


def is_admin(role: Annotated[str, Depends(get_current_user_role)]) -> bool:
    """Verifica se o usuário tem privilégios de administrador."""
    return role == 'admin'


# Dependency pronta para uso nos routers
AdminPermission = Annotated[bool, Depends(is_admin)]
