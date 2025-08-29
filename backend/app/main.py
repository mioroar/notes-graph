from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import engine, get_session
from app.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # """Lifespan события для инициализации и завершения БД."""
    # # Startup
    # try:
    #     async with engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)
    # except Exception:
    #     # Игнорируем ошибки подключения к БД при запуске
    #     pass
    # yield
    # # Shutdown
    # try:
    #     await engine.dispose()
    # except Exception:
        pass


app = FastAPI(title="Notes Graph API")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Проверка состояния API."""
    return {"status": "ok"}


@app.get("/db/health")
async def db_health_check(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """Проверка соединения с базой данных."""
    await session.execute(text("SELECT 1"))
    return {"db": "ok"}
