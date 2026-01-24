from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func  # type: ignore
from sqlalchemy.orm import (  # type: ignore
    Mapped,
    mapped_column,
)

from app_gestao.db.database import Base


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        info={'description': 'Descrição detalhada da demanda administrativa'},
    )
    status: Mapped[str] = mapped_column(
        String(30), default='pending', nullable=False
    )
    priority: Mapped[str] = mapped_column(String(20), default='medium')
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    # RELACIONAMENTOS E REGRAS DE NEGÓCIO

    # Usuário que criou a task (Obrigatório conforme regra de negócio)
    created_by: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False
    )

    # Usuário responsável (Pode ser nulo no momento da criação)
    assigned_to: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id'), nullable=True
    )


def __repr__(self) -> str:
    return (
        f'Task(id={self.id!r}, title={self.title!r}, status={self.status!r})'
    )
