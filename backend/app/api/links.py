from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .dependencies import get_note_service
from app.schemas.note import NoteLinkCreate, NoteLinkResponse, NoteResponse
from app.services.note_service import NoteService

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

@router.post("/", response_model=NoteLinkCreate, status_code=201,
    description="Создание связи между заметками")
async def create_link(link_data: NoteLinkCreate, 
    note_service: NoteService = Depends(get_note_service)) -> NoteLinkCreate:
    try:
        return await note_service.create_link(link_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания связи: {str(e)}")


@router.get("/{link_id}", response_model=NoteLinkResponse, status_code=200,
    description="Получение связи между заметками по ID")
async def get_link_by_id(link_id,
    note_service: NoteService = Depends(get_note_service)) -> NoteLinkResponse:
    try:
        return await note_service.get_link_by_id(link_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения связи: {str(e)}")

@router.get("/by-note/{note_id}", response_model=List[NoteLinkResponse], status_code=200,
    description="Получение связей заметки по участию")
async def get_links_by_participant(note_id,
    note_service: NoteService = Depends(get_note_service)) -> List[NoteLinkResponse]:
    try:
        return await note_service.get_links_by_participant(note_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения связей: {str(e)}")

@router.delete("/{link_id}", response_model=bool, status_code=200,
    description="Удаление связи между заметками по ID")
async def delete_link(link_id,
    note_service: NoteService = Depends(get_note_service)) -> bool:
    try:
        return await note_service.delete_link(link_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления связи: {str(e)}")
