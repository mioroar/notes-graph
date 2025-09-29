from fastapi import APIRouter, Depends, HTTPException
from typing import List
from .dependencies import get_note_service
from app.schemas.note import (
    NoteCreate, NoteUpdate, NoteResponse, NoteWithRelations, 
    NoteWithRelationsOptimized, NoteLinkSummary
)
from app.services.note_service import NoteService

from functools import wraps
from typing import Callable, Any

def handle_errors(operation_name: str):
    """Декоратор для обработки ошибок."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Ошибка {operation_name}: {str(e)}"
                )
        return wrapper
    return decorator

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={
        404: {"description": "Заметка не найдена"},
        422: {"description": "Ошибка валидации данных"}
    }
)

@handle_errors("создания заметки")
@router.post("/", response_model=NoteResponse, status_code=201,
    description="Создание новой заметки")
async def create_note(note: NoteCreate,
    note_service: NoteService = Depends(get_note_service)) -> NoteResponse:
    return await note_service.create_note(note)

@handle_errors("получения заметки")
@router.get("/{note_id}", response_model=NoteResponse, status_code=200,
    description="Получение полной карточки заметки")
async def get_note(note_id: int, 
    note_service: NoteService = Depends(get_note_service)) -> NoteResponse:
    note = await note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note

@handle_errors("получения каталога заметок")
@router.get("/", response_model=List[NoteLinkSummary], status_code=200,
    description="Получение каталога заметок (без контента)")
async def get_notes(skip: int = 0, limit: int = 100,
    note_service: NoteService = Depends(get_note_service)) -> List[NoteLinkSummary]:
    notes = await note_service.get_notes(skip=skip, limit=limit)
    # Преобразуем в упрощенную схему для каталога
    return [
        NoteLinkSummary(id=note.id, title=note.title, importance=note.importance)
        for note in notes
    ]

@handle_errors("получения заметки с связями")
@router.get("/{note_id}/full", response_model=NoteWithRelationsOptimized, status_code=200,
    description="Получение заметки с оптимизированными связанными заметками")
async def get_full_note(
    note_id: int,
    note_service: NoteService = Depends(get_note_service)
) -> NoteWithRelationsOptimized:
    note = await note_service.get_full_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    
    return NoteWithRelationsOptimized(
        **note.__dict__,
        parents=[
            NoteLinkSummary(id=p.id, title=p.title, importance=p.importance) 
            for p in note.parents
        ],
        children=[
            NoteLinkSummary(id=c.id, title=c.title, importance=c.importance) 
            for c in note.children
        ]
    )

@handle_errors("получения предков")
@router.get("/{note_id}/ancestors", response_model=List[NoteResponse], status_code=200,
    description="Получение всех предков заметки")
async def get_ancestors(note_id: int,
    note_service: NoteService = Depends(get_note_service)) -> List[NoteResponse]:
    return await note_service.get_ancestors(note_id)

@handle_errors("получения потомков")
@router.get("/{note_id}/descendants", response_model=List[NoteResponse], status_code=200,
    description="Получение всех потомков заметки")
async def get_descendants(note_id: int,
    note_service: NoteService = Depends(get_note_service)) -> List[NoteResponse]:
    return await note_service.get_descendants(note_id)


@handle_errors("обновления заметки")
@router.put("/{note_id}", response_model=NoteResponse, status_code=200,
    description="Обновление заметки")
async def update_notes(note_id: int, note_data: NoteUpdate,
    note_service: NoteService = Depends(get_note_service)) -> NoteResponse:
    note = await note_service.update_note(note_id, note_data)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note

@handle_errors("удаления заметки")
@router.delete("/{note_id}", response_model=bool, status_code=200,
    description="Удаление заметки")
async def delete_note(
    note_id: int,
    note_service: NoteService = Depends(get_note_service)) -> bool:
    success = await note_service.delete_note(note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return success
