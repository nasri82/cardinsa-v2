

from app.core.database import get_db
from app.modules.benefits.models.coverage_model import Coverage
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional


class CoverageRepository:
    def __init__(self, db: Session):
        self.db = db


def get_all(self) -> List[Coverage]:
    return self.db.query(Coverage).all()


def get_by_id(self, id: UUID) -> Optional[Coverage]:
    return self.db.query(Coverage).filter(Coverage.id == id).first()


def create(self, obj_in: dict) -> Coverage:
    db_obj = Coverage(**obj_in)
    self.db.add(db_obj)
    self.db.commit()
    self.db.refresh(db_obj)
    return db_obj


def update(self, db_obj: Coverage, obj_in: dict) -> Coverage:
    for field, value in obj_in.items():
        setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


def delete(self, id: UUID) -> None:
    obj = self.get_by_id(id)
    if obj:
        self.db.delete(obj)
        self.db.commit()