from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import SETTINGS

engine = create_async_engine(
    SETTINGS.sqlalchemy_url, 
    echo=False, 
    pool_pre_ping=True
)

SessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Зависимость для получения асинхронной сессии БД."""
    async with SessionLocal() as session:
        yield session
