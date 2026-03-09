from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from app.core.database import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: T) -> T:
        self.db.add(obj_in)
        self.db.commit()
        self.db.refresh(obj_in)
        return obj_in

    def update(self, db_obj: T, obj_in: dict) -> T:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> Optional[T]:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
