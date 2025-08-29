FROM python:3.13-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Ставим uv (через pip достаточно)
RUN pip install --no-cache-dir uv

# Сначала зависимости, потом исходники — быстрее кэшируется
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen || uv sync

# Копируем исходный код
COPY . .

# Создаем непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

# Используем переменные окружения для конфигурации
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
