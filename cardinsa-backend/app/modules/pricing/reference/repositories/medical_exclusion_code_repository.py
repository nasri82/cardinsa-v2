from sqlalchemy.orm import Session
from app.modules.pricing.reference.models.medical_exclusion_code_model import MedicalExclusionCode
from app.modules.pricing.reference.schemas.medical_exclusion_code_schema import (
    MedicalExclusionCodeCreate, MedicalExclusionCodeUpdate)


class MedicalExclusionCodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(MedicalExclusionCode).offset(skip).limit(limit).all()

    def get_by_id(self, id):
        return self.db.query(MedicalExclusionCode).filter(MedicalExclusionCode.id == id).first()

    def create(self, obj_in: MedicalExclusionCodeCreate):
        obj = MedicalExclusionCode(**obj_in.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, db_obj: MedicalExclusionCode, obj_in: MedicalExclusionCodeUpdate):
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
