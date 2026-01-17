from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, String, func  # type: ignore
from sqlalchemy.orm import (  # type: ignore
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


class TodoState(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


@mapped_as_dataclass(table_registry)
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    todos: Mapped[list['Todo']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
        init=False,
        repr=False,
        compare=False,
        default_factory=list,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        default='user',
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


@mapped_as_dataclass(table_registry)
class Todo:
    __tablename__ = 'todos'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    state: Mapped[TodoState]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(
        back_populates='todos',
        init=False,
        repr=False,
        compare=False,
    )
