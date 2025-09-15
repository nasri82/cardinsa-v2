from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.models.pricing_deductible_model import PricingDeductible
from app.modules.pricing.modifiers.schemas.pricing_deductible_schema import (
    PricingDeductibleCreate,
    PricingDeductibleUpdate,
)

def get_all(db: Session) -> List[PricingDeductible]:
    return db.query(PricingDeductible).all()

def get_by_id(db: Session, id: UUID) -> Optional[PricingDeductible]:
    return db.query(PricingDeductible).filter(PricingDeductible.id == id).first()

def create(db: Session, data: PricingDeductibleCreate) -> PricingDeductible:
    obj = PricingDeductible(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: PricingDeductible, data: PricingDeductibleUpdate) -> PricingDeductible:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, id: UUID) -> bool:
    obj = get_by_id(db, id)
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False
