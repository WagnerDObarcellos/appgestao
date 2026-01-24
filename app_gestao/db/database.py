from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker  # type: ignore

from app_gestao.core.settings import Settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(Settings().DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
