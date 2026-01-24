from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException  # type: ignore
from sqlalchemy import select  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from app_gestao.core.security import AdminPermission
from app_gestao.db.database import get_session
from app_gestao.models.task import Task
from app_gestao.schemas.task import TaskCreate, TaskSchema, TaskUpdate

router = APIRouter(prefix='/tasks', tags=['Tasks'])

# Alias para a dependência da sessão para encurtar as linhas
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', response_model=TaskSchema, status_code=HTTPStatus.CREATED)
async def create_task(task_data: TaskCreate, db: SessionDep):  # type: ignore
    """
    Cria uma nova task.
    Regra: created_by é obrigatório e assigned_to pode ser nulo.
    """
    new_task = Task(**task_data.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@router.get('/', response_model=List[TaskSchema])
async def list_tasks(db: SessionDep):  # type: ignore
    """Lista todas as tasks cadastradas."""
    result = await db.execute(select(Task))
    return result.scalars().all()


@router.get('/{task_id}', response_model=TaskSchema)
async def get_task(task_id: int, db: SessionDep):  # type: ignore
    """Busca uma task específica pelo ID."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task não encontrada')
    return task


@router.patch(
    '/{task_id}',
    response_model=TaskSchema,
)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: SessionDep,  # type: ignore
    is_admin_user: Annotated[bool, Depends(AdminPermission)],
):
    """
    Atualiza dados de uma task.
    Regra: Apenas administradores podem atribuir responsáveis.
    """
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task não encontrada'
        )

    update_data = task_update.model_dump(exclude_unset=True)

    # O nome aqui deve bater com o parâmetro da função: is_admin_user
    if 'assigned_to' in update_data and not is_admin_user:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Permissão negada: apenas administradores podem '
            'atribuir ou alterar o responsável pela tarefa.',
        )

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete('/{task_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_task(task_id: int, db: SessionDep):  # type: ignore
    """Remove uma task do sistema."""
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task não encontrada'
        )

    await db.delete(task)
    await db.commit()
