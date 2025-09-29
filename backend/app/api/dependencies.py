from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.note_service import NoteService
from typing import AsyncGenerator

async def get_note_service(db: AsyncSession = Depends(get_session)) -> AsyncGenerator[NoteService, None]:
   
   yield NoteService(db)