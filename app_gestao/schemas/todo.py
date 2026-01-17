from typing import Optional

from pydantic import BaseModel, Field  # type: ignore

from app_gestao.models import TodoState

from .common import FilterPage


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublic(TodoSchema):
    id: int


class TodoList(BaseModel):
    todos: list[TodoPublic]


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[TodoState] = None


class FilterTodo(FilterPage):
    title: Optional[str] = Field(None, min_length=3, max_length=20)
    description: Optional[str] = Field(None, min_length=3, max_length=20)
    state: Optional[TodoState] = None
