from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, func  # type: ignore
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore

from app_gestao.db.database import Base

if TYPE_CHECKING:
    from app_gestao.models.todo import Todo


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)

    role: Mapped[str] = mapped_column(
        String(20),
        default='user',
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )

    todos: Mapped[list['Todo']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
