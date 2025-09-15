from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from app.modules.org.models.company_model import Company
from app.modules.org.schemas.company_schema import CompanyCreate, CompanyUpdate

def list_all(db: Session) -> list[Company]:
    return list(db.scalars(select(Company).order_by(Company.name)))

def get(db: Session, company_id: UUID) -> Company | None:
    return db.get(Company, company_id)

def create(db: Session, payload: CompanyCreate) -> Company:
    obj = Company(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update(db: Session, company: Company, payload: CompanyUpdate) -> Company:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(company, k, v)
    db.add(company); db.commit(); db.refresh(company)
    return company

def delete(db: Session, company: Company) -> None:
    db.delete(company); db.commit()
