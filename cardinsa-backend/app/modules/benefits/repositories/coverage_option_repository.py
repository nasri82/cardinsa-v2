

from app.core.database import get_db
from app.modules.benefits.models.coverage_option_model import CoverageOption
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional


class CoverageOptionRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_all(self) -> List[CoverageOption]:
        return self.db.query(CoverageOption).all()


    def get_by_id(self, id: UUID) -> Optional[CoverageOption]:
        return self.db.query(CoverageOption).filter(CoverageOption.id == id).first()


    def create(self, obj_in: dict) -> CoverageOption:
        db_obj = CoverageOption(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def update(self, db_obj: CoverageOption, obj_in: dict) -> CoverageOption:
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