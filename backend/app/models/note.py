from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, UniqueConstraint, CheckConstraint, func, Index
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

from typing import Optional


class Note(Base):
    """Модель заметки в графе.
    
    Представляет собой узел в графе заметок с возможностью создания иерархических связей.
    Каждая заметка может иметь родительские и дочерние заметки через модель NoteLink.
    """
    # Основные поля заметки
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="Заголовок заметки")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Содержимое заметки")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Время создания")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
                                                 nullable=False, comment="Время последнего обновления")
    # Ограничения и индексы
    __table_args__ = (
        CheckConstraint("length(btrim(title)) > 0", name="ck_note_title_not_empty"),  # Заголовок не может быть пустым
        Index("ix_note_title", "title"),  # Индекс для быстрого поиска по заголовку
        Index("ix_note_title_lower", func.lower(title)),  # Индекс для регистронезависимого поиска
    )
    # Связи с другими заметками (иерархия)
    parent_links: Mapped[list["NoteLink"]] = relationship(
        back_populates="child",
        cascade="all, delete-orphan",  # Удаляем связи при удалении заметки
        foreign_keys="NoteLink.child_id",
        lazy="selectin",  # Загружаем связи вместе с заметкой
    )
    children_links: Mapped[list["NoteLink"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",  # Удаляем связи при удалении заметки
        foreign_keys="NoteLink.parent_id",
        lazy="selectin",  # Загружаем связи вместе с заметкой
    )

    # Свойства для удобного доступа к связанным заметкам
    @property
    def parents(self) -> list["Note"]:
        """Получить список родительских заметок."""
        return [link.parent for link in self.parent_links]

    @property
    def children(self) -> list["Note"]:
        """Получить список дочерних заметок."""
        return [link.child for link in self.children_links]

    def __repr__(self) -> str:
        """Строковое представление заметки."""
        return f"<Note(id={self.id}, title='{self.title}')>"


class NoteLink(Base):
    """Модель связи между заметками.
    
    Представляет иерархическую связь между двумя заметками.
    Родительская заметка содержит дочернюю как подтему или связанную идею.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("note.id", ondelete="CASCADE"), nullable=False, index=True, comment="ID родительской заметки")
    child_id: Mapped[int] = mapped_column(ForeignKey("note.id", ondelete="CASCADE"), nullable=False, index=True, comment="ID дочерней заметки")

    # Ограничения для корректности связей
    __table_args__ = (
        UniqueConstraint("parent_id", "child_id", name="uq_note_link"),  # Уникальная связь между двумя заметками
        CheckConstraint("parent_id <> child_id", name="ck_no_self_link"),  # Заметка не может ссылаться сама на себя
    )

    # Связи с заметками
    parent: Mapped["Note"] = relationship(
        back_populates="children_links",
        foreign_keys="NoteLink.parent_id",
        lazy="joined",  # Загружаем связанную заметку сразу
    )
    child: Mapped["Note"] = relationship(
        back_populates="parent_links",
        foreign_keys="NoteLink.child_id",
        lazy="joined",  # Загружаем связанную заметку сразу
    )

    def __repr__(self) -> str:
        """Строковое представление связи между заметками."""
        return f"<NoteLink(parent_id={self.parent_id}, child_id={self.child_id})>"