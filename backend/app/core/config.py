import os
from typing import Final

from dotenv import load_dotenv
from pydantic import BaseModel

# Загружаем .env файл
load_dotenv()


class Settings(BaseModel):
    """Настройки приложения."""
    
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    app_port: int = 8000
    
    @property
    def sqlalchemy_url(self) -> str:
        """URL для подключения к базе данных."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


def get_settings() -> Settings:
    """Получение настроек из переменных окружения."""
    return Settings(
        postgres_host=os.getenv("POSTGRES_HOST", "db"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        postgres_db=os.getenv("POSTGRES_DB", "notes"),
        postgres_user=os.getenv("POSTGRES_USER", "notes"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "notes"),
        app_port=int(os.getenv("APP_PORT", "8000")),
    )


SETTINGS: Final[Settings] = get_settings()
