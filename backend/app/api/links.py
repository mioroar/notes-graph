from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .dependencies import get_note_service
from app.schemas.note import NoteLinkCreate, NoteLinkResponse, NoteResponse
from app.services.note_service import NoteService

from functools import wraps
from typing import Callable, Any

# def handle_errors(operation_name: str):
#     """Декоратор для обработки ошибок."""
#     def decorator(func: Callable) -> Callable:
#         @wraps(func)
#         async def wrapper(*args, **kwargs) -> Any:
#             try:
#                 return await func(*args, **kwargs)
#             except HTTPException:                                      ТУДУ
#                 raise
#             except Exception as e:
#                 raise HTTPException(
#                     status_code=500, 
#                     detail=f"Ошибка {operation_name}: {str(e)}"
#                 )
#         return wrapper
#     return decorator

router = APIRouter(
    prefix="/links",
    tags=["links"],
    responses={
        404: {"description": "Заметка не найдена"},
        422: {"description": "Ошибка валидации данных"}
    }
)

@router.post("/", response_model=NoteLinkResponse, status_code=201,
    description="Создание связи между заметками")
async def create_link(link_data: NoteLinkResponse, 
    note_service: NoteService = Depends(get_note_service)) -> NoteLinkResponse:
    try:
        link = await note_service.create_link(link_data)
        if not link:
            raise HTTPException(status_code=400, detail="Связь не создана")
        return link
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания связи: {str(e)}")


@router.get("/{link_id}", response_model=NoteLinkResponse, status_code=200,
    description="Получение связи между заметками по ID")
async def get_link_by_id(link_id: int,
    note_service: NoteService = Depends(get_note_service)) -> NoteLinkResponse:
    try:
        link = await note_service.get_link_by_id(link_id)
        if not link:
            raise HTTPException(status_code=404, detail="Связь не найдена")
        return link
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения связи: {str(e)}")

@router.get("/by-note/{note_id}", response_model=List[NoteLinkResponse], status_code=200,
    description="Получение связей заметки по участию")
async def get_links_by_participant(note_id: int,
    note_service: NoteService = Depends(get_note_service)) -> List[NoteLinkResponse]:
    try:
        return await note_service.get_links_by_participant(note_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения связей: {str(e)}")

@router.delete("/{link_id}", response_model=bool, status_code=200,
    description="Удаление связи между заметками по ID")
async def delete_link(link_id: int,
    note_service: NoteService = Depends(get_note_service)) -> bool:
    try:
        success = await note_service.delete_link(link_id)
        if not success:
            raise HTTPException(status_code=404, detail="Связь не найдена")
        return success
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления связи: {str(e)}")
