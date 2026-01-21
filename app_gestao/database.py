from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase  # type: ignore

from app_gestao.settings import Settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
