from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from app.modules.org.models.unit_model import Unit
from app.modules.org.schemas.unit_schema import UnitCreate, UnitUpdate

def list_all(db: Session, department_id: UUID | None = None) -> list[Unit]:
    stmt = select(Unit).order_by(Unit.name)
    if department_id:
        stmt = stmt.where(Unit.department_id == department_id)
    return list(db.scalars(stmt))

def get(db: Session, unit_id: UUID) -> Unit | None:
    return db.get(Unit, unit_id)

def create(db: Session, payload: UnitCreate) -> Unit:
    obj = Unit(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update(db: Session, unit: Unit, payload: UnitUpdate) -> Unit:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(unit, k, v)
    db.add(unit); db.commit(); db.refresh(unit)
    return unit

def delete(db: Session, unit: Unit) -> None:
    db.delete(unit); db.commit()
