import asyncio
from logging.config import fileConfig
from typing import Optional

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import SETTINGS
from app.models.base import Base
import app.models  # noqa: F401  # важно: регистрирует Note/NoteLink в metadata

# Alembic Config — доступ к параметрам из alembic.ini
config = context.config

# Логирование Alembic (берёт настройки из alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для автогенерации
target_metadata = Base.metadata


def get_url() -> str:
    """Возвращает DSN для подключения Alembic.

    Returns:
        str: Строка подключения SQLAlchemy в async-формате (postgresql+asyncpg://...).
    """
    return SETTINGS.sqlalchemy_url


def run_migrations_offline() -> None:
    """Запускает миграции в offline-режиме.

    Конфигурирует Alembic на работу только по URL без создания Engine.
    Полезно для генерации SQL-скриптов миграций.
    """
    url: str = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполняет миграции, используя переданное соединение.

    Args:
        connection (Connection): Синхронное соединение SQLAlchemy,
            проброшенное из async-контекста.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создаёт async-движок и запускает online-миграции.

    URL подставляется из настроек приложения, чтобы единообразно
    использовать .env/Settings.
    """
    # Вписываем URL в конфиг Alembic перед созданием движка
    config.set_main_option("sqlalchemy.url", get_url())

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запускает миграции в online-режиме (через реальное подключение)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
