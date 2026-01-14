from http import HTTPStatus

from fastapi import FastAPI  # type: ignore

from app_gestao.routers import auth, todos, users
from app_gestao.schemas import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
async def read_root():
    return {'message': 'Olá, mundo!'}
