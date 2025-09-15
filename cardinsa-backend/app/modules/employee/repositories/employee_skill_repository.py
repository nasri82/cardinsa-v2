from sqlalchemy.orm import Session
from uuid import UUID
from app.models import employee_skill_model
from app.schemas import employee_skill_schema


class EmployeeSkillRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(employee_skill_model.EmployeeSkill).all()

    @staticmethod
    def create(db: Session, payload: employee_skill_schema.EmployeeSkillCreate):
        db_obj = employee_skill_model.EmployeeSkill(**payload.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, item_id: UUID, payload: employee_skill_schema.EmployeeSkillUpdate):
        db_obj = db.query(employee_skill_model.EmployeeSkill).filter(employee_skill_model.EmployeeSkill.id == item_id).first()
        if db_obj:
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, item_id: UUID):
        db_obj = db.query(employee_skill_model.EmployeeSkill).filter(employee_skill_model.EmployeeSkill.id == item_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj