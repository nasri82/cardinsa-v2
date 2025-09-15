from sqlalchemy.orm import Session
from app.modules.pricing.reference.models.cpt_code_model import CPTCode
from app.modules.pricing.reference.schemas.cpt_code_schema import CPTCodeCreate, CPTCodeUpdate


class CPTCodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(CPTCode).offset(skip).limit(limit).all()

    def get_by_id(self, id):
        return self.db.query(CPTCode).filter(CPTCode.id == id).first()

    def create(self, obj_in: CPTCodeCreate):
        obj = CPTCode(**obj_in.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, db_obj: CPTCode, obj_in: CPTCodeUpdate):
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
