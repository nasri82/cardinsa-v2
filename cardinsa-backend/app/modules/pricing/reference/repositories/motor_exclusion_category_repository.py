from sqlalchemy.orm import Session
from app.modules.pricing.reference.models.motor_exclusion_category_model import MotorExclusionCategory
from app.modules.pricing.reference.schemas.motor_exclusion_category_schema import (
    MotorExclusionCategoryCreate, MotorExclusionCategoryUpdate)


class MotorExclusionCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(MotorExclusionCategory).offset(skip).limit(limit).all()

    def get_by_id(self, id):
        return self.db.query(MotorExclusionCategory).filter(MotorExclusionCategory.id == id).first()

    def create(self, obj_in: MotorExclusionCategoryCreate):
        obj = MotorExclusionCategory(**obj_in.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, db_obj: MotorExclusionCategory, obj_in: MotorExclusionCategoryUpdate):
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id):
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
