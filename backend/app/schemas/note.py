from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class NoteBase(BaseModel):
    """Базовая схема заметки.
    
    Содержит общие поля для создания и обновления заметок.
    Все схемы заметок наследуются от этого базового класса.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Заголовок заметки"
    )
    content: Optional[str] = Field(
        None,
        description="Содержимое заметки"
    )
    importance: Optional[int] = Field(
        None,
        ge=0,
        le=9,
        description="Важность заметки от 0 до 9"
    )


class NoteCreate(NoteBase):
    """Схема для создания новой заметки.
    
    Наследует все поля от NoteBase. Все поля обязательные
    (кроме content и importance, которые могут быть None).
    """
    pass


class NoteUpdate(BaseModel):
    """Схема для обновления существующей заметки.
    
    Все поля опциональные, что позволяет обновлять
    только нужные атрибуты заметки.
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Новый заголовок заметки"
    )
    content: Optional[str] = Field(
        None,
        description="Новое содержимое заметки"
    )
    importance: Optional[int] = Field(
        None,
        ge=0,
        le=9,
        description="Новая важность заметки от 0 до 9"
    )


class NoteResponse(NoteBase):
    """Схема для ответа с заметкой.
    
    Содержит все поля заметки включая системные
    (id, created_at, updated_at).
    """
    id: int = Field(..., description="Уникальный идентификатор заметки")
    created_at: datetime = Field(..., description="Время создания заметки")
    updated_at: datetime = Field(..., description="Время последнего обновления заметки")

    class Config:
        from_attributes = True


class NoteLinkCreate(BaseModel):
    """Схема для создания связи между заметками.
    
    Представляет иерархическую связь где parent_id
    является родительской заметкой, а child_id - дочерней.
    """
    parent_id: int = Field(..., description="ID родительской заметки")
    child_id: int = Field(..., description="ID дочерней заметки")


class NoteLinkResponse(BaseModel):
    """Схема для ответа со связью между заметками.
    
    Содержит информацию о существующей связи
    между двумя заметками.
    """
    id: int = Field(..., description="Уникальный идентификатор связи")
    parent_id: int = Field(..., description="ID родительской заметки")
    child_id: int = Field(..., description="ID дочерней заметки")

    class Config:
        from_attributes = True


class NoteLinkSummary(BaseModel):
    """Упрощенная схема заметки для боковой панели.
    
    Содержит только необходимые поля для отображения в списке связанных заметок.
    Исключает content, created_at, updated_at для экономии трафика.
    """
    id: int = Field(..., description="ID заметки")
    title: str = Field(..., description="Заголовок заметки")
    importance: Optional[int] = Field(None, description="Важность заметки")
    
    class Config:
        from_attributes = True


class NoteWithRelations(NoteResponse):
    """Схема заметки с полной информацией о связанных заметках.
    
    Расширяет NoteResponse, добавляя списки родительских
    и дочерних заметок со всеми их полями.
    
    default_factory=list каждый экземпляр получает СВОЙ список
    
    Attributes:
        parents: Список родительских заметок с полными данными
        children: Список дочерних заметок с полными данными
    """
    parents: List["NoteResponse"] = Field(
        default_factory=list, 
        description="Список родительских заметок"
    )
    children: List["NoteResponse"] = Field(
        default_factory=list, 
        description="Список дочерних заметок"
    )


class NoteWithRelationsOptimized(NoteResponse):
    """Оптимизированная схема заметки с упрощенными связями.
    
    Основная заметка содержит полную информацию,
    связанные заметки - только необходимые поля для боковой панели.
    Значительно уменьшает размер ответа API.
    """
    parents: List[NoteLinkSummary] = Field(
        default_factory=list,
        description="Родительские заметки (только ID, title, importance)"
    )
    children: List[NoteLinkSummary] = Field(
        default_factory=list,
        description="Дочерние заметки (только ID, title, importance)"
    )