from sqlalchemy.orm import Session
from uuid import UUID
from app.models import employee_model
from app.schemas import employee_schema


class EmployeeRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(employee_model.Employee).all()

    @staticmethod
    def create(db: Session, payload: employee_schema.EmployeeCreate):
        db_obj = employee_model.Employee(**payload.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, item_id: UUID, payload: employee_schema.EmployeeUpdate):
        db_obj = db.query(employee_model.Employee).filter(employee_model.Employee.id == item_id).first()
        if db_obj:
            for key, value in payload.dict(exclude_unset=True).items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, item_id: UUID):
        db_obj = db.query(employee_model.Employee).filter(employee_model.Employee.id == item_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj