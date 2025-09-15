from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.modules.pricing.modifiers.models.pricing_commission_model import PricingCommission
from app.modules.pricing.modifiers.schemas.pricing_commission_schema import (
    PricingCommissionCreate,
    PricingCommissionUpdate,
)

def get_all(db: Session) -> List[PricingCommission]:
    return db.query(PricingCommission).all()

def get_by_id(db: Session, id: UUID) -> Optional[PricingCommission]:
    return db.query(PricingCommission).filter(PricingCommission.id == id).first()

def create(db: Session, data: PricingCommissionCreate) -> PricingCommission:
    obj = PricingCommission(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, db_obj: PricingCommission, data: PricingCommissionUpdate) -> PricingCommission:
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
