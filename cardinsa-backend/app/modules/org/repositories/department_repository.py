from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from app.modules.org.models.department_model import Department
from app.modules.org.schemas.department_schema import DepartmentCreate, DepartmentUpdate

def list_all(db: Session, company_id: UUID | None = None) -> list[Department]:
    stmt = select(Department).order_by(Department.name)
    if company_id:
        stmt = stmt.where(Department.company_id == company_id)
    return list(db.scalars(stmt))

def get(db: Session, department_id: UUID) -> Department | None:
    return db.get(Department, department_id)

def create(db: Session, payload: DepartmentCreate) -> Department:
    obj = Department(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update(db: Session, department: Department, payload: DepartmentUpdate) -> Department:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(department, k, v)
    db.add(department); db.commit(); db.refresh(department)
    return department

def delete(db: Session, department: Department) -> None:
    db.delete(department); db.commit()
