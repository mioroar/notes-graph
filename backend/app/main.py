from typing import Dict

from fastapi import FastAPI


app = FastAPI(
    title="Notes Graph API",
    version="0.1.0",
    description="Бэкенд для заметок в виде графа.",
)


@app.get("/health")
def health() -> Dict[str, str]:
    """Проверка живости сервера.

    Returns:
        Dict[str, str]: Простой JSON-ответ со статусом сервиса.
    """
    return {"status": "ok"}
