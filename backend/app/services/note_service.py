from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, func, select, update
from sqlalchemy.orm import selectinload

from app.models.note import Note, NoteLink
from app.schemas.note import NoteCreate, NoteUpdate, NoteLinkCreate

class NoteService:
    def __init__(self, db: AsyncSession):
        # Инициализация с сессией БД
        self.db = db
        
    async def create_note(self, note_data: NoteCreate) -> Note:
        # Создание заметки
        new_note = Note(**note_data.model_dump())#Pydantic схема → Словарь → SQLAlchemy объект
        
        self.db.add(new_note)
        await self.db.commit()
        await self.db.refresh(new_note)

        return new_note

    async def get_note(self, note_id: int) -> Optional[Note]:
        # Получение заметки по ID
        result = await self.db.execute(select(Note).where(Note.id == note_id))
        return result.scalar_one_or_none()

    async def get_full_note(self, note_id: int) -> Optional[Note]:
        """Получить заметку с загруженными связями для NoteWithRelations.
    
        Args:
          note_id: ID заметки
        
        Returns:
          Note с загруженными parent_links и children_links, или None если не найдена
        """
    # Используем selectinload для загрузки связей одним запросом
        result = await self.db.execute(
            select(Note)
            .options(
                selectinload(Note.parent_links).selectinload(NoteLink.parent),
                selectinload(Note.children_links).selectinload(NoteLink.child)
            )
            .where(Note.id == note_id)
        )
        return result.scalar_one_or_none()
    
    async def get_notes(self, skip: int = 0, limit: int = 100) -> List[Note]:
        # Получение списка заметок

        result = await self.db.execute(select(Note).offset(skip).limit(limit))
        return result.scalars().all()

    
    async def update_note(self, note_id: int, 
                          note_data: NoteUpdate) -> Optional[Note]:
        # Обновление заметки
        new_data = note_data.model_dump(exclude_unset=True)
        result = await self.db.execute(update(Note)
                                        .where(Note.id == note_id)
                                        .values(**new_data).returning(Note))
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def delete_note(self, note_id: int) -> bool:
        # Удаление заметки
        for_delete = await self.get_note(note_id)
        
        if for_delete is None:
            return False
        else:
            await self.db.delete(for_delete)
            await self.db.commit()
            return True

    
    async def create_link(self, link_data: NoteLinkCreate) -> Optional[NoteLink]:
        if await self.check_circular_reference(link_data.parent_id, link_data.child_id):
            return None
        # Создание связи между заметками
        # if link_data.parent_id == link_data.child_id:
        #     return None
        parent = await self.get_note(link_data.parent_id)
        child = await self.get_note(link_data.child_id)
        
        # exists = await self.db.execute(select(NoteLink).where(
        #     and_(NoteLink.parent_id == link_data.parent_id,
        #          NoteLink.child_id == link_data.child_id))
        # ).scalar_one_or_none()

        result = await self.db.execute(select(NoteLink).where(
        and_(NoteLink.parent_id == link_data.parent_id,
             NoteLink.child_id == link_data.child_id)))
        exists = result.scalar_one_or_none()    
        
        if parent and child and exists is None:
            new_link = NoteLink(**link_data.model_dump())
            self.db.add(new_link)
            await self.db.commit()
            await self.db.refresh(new_link)
            return new_link
        
        return None
        
    async def get_links_by_participant(self, note_id: int) -> List[NoteLink]:
        result = await self.db.execute(
            select(NoteLink).where(
                or_(
                    NoteLink.parent_id == note_id,  # Заметка как родитель
                    NoteLink.child_id == note_id     # Заметка как ребенок
                )))
        return result.scalars().all()
    
    async def get_link_by_id(self, link_id: int) -> Optional[NoteLink]:
        result = await self.db.execute(select(NoteLink).where(NoteLink.id == link_id))
        return result.scalar_one_or_none()
    
    async def delete_link(self, link_id: int) -> bool:
        for_delete = await self.get_link_by_id(link_id)
        if for_delete is None:
            return False
        else:
            await self.db.delete(for_delete)
            await self.db.commit()
            return True

    async def get_ancestors(self, note_id: int) -> List[Note]:
        """Получить всех предков заметки."""
        note = await self.get_note(note_id)
        if not note:
            return []

        parents = note.parents
        ancestors = []

        for parent in parents:
            ancestors.append(parent)
            parent_ancestors = await self.get_ancestors(parent.id)
            ancestors.extend(parent_ancestors)

        return ancestors

    async def get_descendants(self, note_id: int) -> List[Note]:
        note = await self.get_note(note_id)
        if not note:
            return []

        children = note.children
        descendants = []

        for child in children:
            descendants.append(child)
            child_descendants = await self.get_descendants(child.id)
            descendants.extend(child_descendants)

        return descendants

    async def check_circular_reference(self, parent_id: int, child_id: int) -> bool:
        if parent_id == child_id:
            return True

        ancestors = await self.get_ancestors(child_id)

        if parent_id in [ancestor.id for ancestor in ancestors]:
            return True
        
        return False
