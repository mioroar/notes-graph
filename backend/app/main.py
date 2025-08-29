from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, get_session
from app.models.base import Base


class HealthOut(BaseModel):
    """Модель ответа для проверки состояния API."""
    status: str


class DBHealthOut(BaseModel):
    """Модель ответа для проверки соединения с БД."""
    db: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Инициализация БД на старте и корректное завершение соединений.

    Создаёт таблицы согласно метаданным ORM и закрывает пул соединений при остановке.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Notes Graph API", version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthOut)
def health_check() -> HealthOut:
    """Возвращает статус готовности веб-приложения.

    Returns:
        HealthOut: Объект со статусом сервиса.
    """
    return HealthOut(status="ok")


@app.get("/db/health", response_model=DBHealthOut)
async def db_health_check(session: AsyncSession = Depends(get_session)) -> DBHealthOut:
    """Проверяет доступность подключения к базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy из зависимостей FastAPI.

    Returns:
        DBHealthOut: Объект со статусом подключения к БД.
    """
    await session.execute(text("SELECT 1"))
    return DBHealthOut(db="ok")
