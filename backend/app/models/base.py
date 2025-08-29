from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Базовый класс для всех ORM моделей."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Автоматическое именование таблиц по имени класса."""
        return cls.__name__.lower()
