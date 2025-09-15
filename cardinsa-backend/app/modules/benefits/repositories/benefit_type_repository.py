from app.modules.benefits.models.benefit_type_model import BenefitType
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional


class BenefitTypeRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_all(self) -> List[BenefitType]:
        return self.db.query(BenefitType).all()


    def get_by_id(self, id: UUID) -> Optional[BenefitType]:
        return self.db.query(BenefitType).filter(BenefitType.id == id).first()


    def create(self, obj_in: dict) -> BenefitType:
        db_obj = BenefitType(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def update(self, db_obj: BenefitType, obj_in: dict) -> BenefitType:
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