from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field  # type: ignore


class TaskBase(BaseModel):
    """Campos base compartilhados entre os schemas."""

    title: str = Field(
        ..., max_length=100, description='Título curto da tarefa'
    )
    description: Optional[str] = Field(
        None, description='Descrição detalhada da demanda administrativa'
    )
    status: str = Field('pending', description='Estado atual da task')
    priority: str = Field('medium', description='Nível de prioridade')
    due_date: Optional[datetime] = Field(None, description='Data limite')


class TaskCreate(TaskBase):
    """Schema para criação de uma nova Task."""

    # created_by é obrigatório conforme regra de negócio
    created_by: int = Field(..., description='ID do usuário que criou a task')
    # assigned_to pode ser nulo no momento da criação
    assigned_to: Optional[int] = Field(None, description='ID do responsável')


class TaskUpdate(BaseModel):
    """Schema para atualização (todos os campos opcionais)."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


class TaskSchema(TaskBase):
    """Schema completo para retorno de dados (Output)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    assigned_to: Optional[int]
