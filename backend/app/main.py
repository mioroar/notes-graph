from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, get_session
# from app.models.base import Base  # больше не нужно

class HealthOut(BaseModel):
    """Модель ответа для проверки состояния API."""
    status: str

class DBHealthOut(BaseModel):
    """Модель ответа для проверки соединения с БД."""
    db: str

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Корректное завершение соединений с БД при остановке приложения."""
    # ВАЖНО: никаких create_all здесь — схему управляет Alembic
    yield
    await engine.dispose()

app = FastAPI(title="Notes Graph API", version="0.1.0", lifespan=lifespan)

@app.get("/health", response_model=HealthOut)
def health_check() -> HealthOut:
    """Проверка готовности веб-приложения."""
    return HealthOut(status="ok")

@app.get("/db/health", response_model=DBHealthOut)
async def db_health_check(session: AsyncSession = Depends(get_session)) -> DBHealthOut:
    """Проверка доступности подключения к базе данных."""
    await session.execute(text("SELECT 1"))
    return DBHealthOut(db="ok")
