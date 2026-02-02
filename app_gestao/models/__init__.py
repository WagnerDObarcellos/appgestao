# app_gestao/models/__init__.py
from .task import Task
from .todos import Todo, TodoState
from .user import (
    User,  # Ajuste '.user' para o nome real do arquivo (ex: .usuarios)
)

# Isso permite que você importe de app_gestao.models diretamente
__all__ = ['User', 'Task', 'Todo', 'TodoState']
